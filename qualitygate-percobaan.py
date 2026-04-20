import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime
import io

# =====================================================
# PAGE CONFIG
# =====================================================
st.set_page_config(
    page_title="Quality Gate Monitoring",
    layout="wide"
)

# =====================================================
# PROFESSIONAL DARK CSS (Refined)
# =====================================================
st.markdown("""
<style>
.stApp {
    background-color: #0d1117;
    color: #e6edf3;
}
section[data-testid="stSidebar"] {
    background-color: #161b22;
    border-right: 1px solid #30363d;
}
h1, h2, h3 {
    color: #f0f6fc !important;
    font-weight: 700;
}
label, p, span {
    color: #c9d1d9 !important;
}
/* Input Fields */
.stTextInput input, .stSelectbox div, .stDateInput input, .stNumberInput input {
    background-color: #21262d !important;
    color: white !important;
    border: 1px solid #30363d !important;
    border-radius: 6px !important;
}
/* Buttons */
.stButton button {
    width: 100%;
    background-color: #238636;
    color: white;
    border: none;
    border-radius: 6px;
    padding: 0.5rem;
}
.stButton button:hover {
    background-color: #2ea043;
    color: white;
}
/* Metrics */
[data-testid="metric-container"] {
    background-color: #161b22;
    border: 1px solid #30363d;
    padding: 15px;
    border-radius: 8px;
}
[data-testid="stMetricValue"] {
    color: #58a6ff !important;
}
/* Table / DataFrame */
[data-testid="stDataFrame"] {
    border: 1px solid #30363d;
}
</style>
""", unsafe_allow_html=True)

# =====================================================
# INITIALIZATION
# =====================================================
COLUMNS = ["No", "Tanggal", "Shift", "No HP", "Layer HP", "Kode Mold", "No Lot", "Keterangan"]

if "db" not in st.session_state:
    st.session_state["db"] = pd.DataFrame(columns=COLUMNS)

st.title("Quality Gate Preform Monitoring System")

# =====================================================
# SIDEBAR: DATA MANAGEMENT
# =====================================================
st.sidebar.header("Data Management")

# Upload File
uploaded_file = st.sidebar.file_uploader("Upload Excel Rekap", type=["xlsx"])
if uploaded_file:
    try:
        df_upload = pd.read_excel(uploaded_file)
        # Cleaning column names
        df_upload.columns = [str(c).strip() for c in df_upload.columns]
        
        # Ensure all required columns exist
        for col in COLUMNS:
            if col not in df_upload.columns:
                df_upload[col] = ""
        
        # Format Tanggal agar seragam (datetime.date)
        df_upload["Tanggal"] = pd.to_datetime(df_upload["Tanggal"], errors='coerce').dt.date
        
        # Reorder and reset No
        df_upload = df_upload[COLUMNS]
        df_upload["No"] = range(1, len(df_upload) + 1)
        
        st.session_state["db"] = df_upload
        st.sidebar.success("Sinkronisasi file berhasil")
    except Exception as e:
        st.sidebar.error(f"Error Upload: {e}")

# Input Data Form
st.sidebar.markdown("---")
st.sidebar.header("Input Data Baru")
with st.sidebar.form("form_input", clear_on_submit=True):
    tgl = st.date_input("Tanggal", datetime.today())
    shift = st.selectbox("Shift", [1, 2, 3])
    hp = st.selectbox("No HP", [f"HP{i:02d}" for i in range(1, 31)])
    layer = st.selectbox("Layer HP", [1, 2, 3, 4, 5])
    mold = st.text_input("Kode Mold")
    lot = st.text_input("No Lot")
    ket = st.selectbox("Keterangan", ["OK", "Visual", "Dimensi", "Visual Dimensi"])
    
    submit = st.form_submit_button("Simpan Baris Baru")
    
    if submit:
        # Get current DB
        current_db = st.session_state["db"].copy()
        
        # Create new row
        new_row = pd.DataFrame([{
            "Tanggal": tgl, # datetime.date object
            "Shift": shift,
            "No HP": hp,
            "Layer HP": layer,
            "Kode Mold": mold,
            "No Lot": lot,
            "Keterangan": ket
        }])
        
        # Combine
        combined = pd.concat([current_db.drop(columns=["No"], errors="ignore"), new_row], ignore_index=True)
        combined["No"] = range(1, len(combined) + 1)
        
        st.session_state["db"] = combined
        st.rerun()

# =====================================================
# DATA PROCESSING
# =====================================================
df_raw = st.session_state["db"].copy()

if df_raw.empty:
    st.info("Silakan unggah file Excel atau input data melalui sidebar untuk memulai.")
    st.stop()

# Tambahkan kolom pembantu untuk analisis
df_raw["is_ng"] = df_raw["Keterangan"].astype(str).str.upper().ne("OK").astype(int)
# Pastikan kolom tanggal adalah objek date untuk filter
df_raw["Tanggal_DT"] = pd.to_datetime(df_raw["Tanggal"]).dt.date

# =====================================================
# DASHBOARD FILTERS
# =====================================================
st.subheader("Filter Dashboard")
c1, c2, c3, c4 = st.columns(4)

with c1:
    f_shift = st.multiselect("Shift", sorted(df_raw["Shift"].unique()))
with c2:
    f_hp = st.multiselect("No HP", sorted(df_raw["No HP"].unique()))
with c3:
    f_ket = st.multiselect("Keterangan", ["OK", "Visual", "Dimensi", "Visual Dimensi"])
with c4:
    f_date = st.date_input("Rentang Tanggal", [])

# Apply Filters
df_f = df_raw.copy()
if f_shift:
    df_f = df_f[df_f["Shift"].isin(f_shift)]
if f_hp:
    df_f = df_f[df_f["No HP"].isin(f_hp)]
if f_ket:
    df_f = df_f[df_f["Keterangan"].isin(f_ket)]
if len(f_date) == 2:
    df_f = df_f[(df_f["Tanggal_DT"] >= f_date[0]) & (df_f["Tanggal_DT"] <= f_date[1])]

# =====================================================
# KPI SECTION
# =====================================================
total = len(df_f)
ng = int(df_f["is_ng"].sum())
ok = total - ng
ng_rate = (ng / total) if total > 0 else 0

k1, k2, k3 = st.columns(3)
k1.metric("Total Check", f"{total} Unit")
k2.metric("Total NG", f"{ng} Unit")
k3.metric("Proporsi NG (%)", f"{ng_rate:.2%}")

# =====================================================
# TOP 5 MACHINES TABLE
# =====================================================
st.markdown("---")
st.subheader("Top 5 Mesin Hotpress dengan NG Tertinggi")

top5 = (
    df_f.groupby("No HP")["is_ng"]
    .sum()
    .reset_index()
    .rename(columns={"No HP": "ID Mesin", "is_ng": "Jumlah Unit NG"})
    .sort_values(by="Jumlah Unit NG", ascending=False)
    .head(5)
)
top5.index = range(1, len(top5) + 1)

if not top5.empty and top5["Jumlah Unit NG"].sum() > 0:
    st.table(top5)
else:
    st.write("Tidak ada data NG ditemukan pada filter ini.")

# =====================================================
# CHARTS
# =====================================================
st.markdown("---")
g1, g2 = st.columns(2)

with g1:
    st.subheader("Grafik NG per Mesin")
    mesin_chart = df_f.groupby("No HP")["is_ng"].sum().reset_index()
    fig1 = px.bar(mesin_chart, x="No HP", y="is_ng", template="plotly_dark", 
                 labels={"is_ng": "Jumlah NG", "No HP": "ID Mesin"},
                 color_discrete_sequence=['#58a6ff'])
    fig1.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
    st.plotly_chart(fig1, use_container_width=True)

with g2:
    st.subheader("Komposisi Jenis Defect")
    ng_only = df_f[df_f["is_ng"] == 1]
    if not ng_only.empty:
        cacat_pie = ng_only["Keterangan"].value_counts().reset_index()
        cacat_pie.columns = ["Jenis", "Total"]
        fig2 = px.pie(cacat_pie, names="Jenis", values="Total", template="plotly_dark", hole=0.4)
        fig2.update_layout(paper_bgcolor='rgba(0,0,0,0)')
        st.plotly_chart(fig2, use_container_width=True)
    else:
        st.write("Belum ada data defect untuk ditampilkan.")

# =========================
# MANAGEMENT TABLE
# =========================
st.markdown("---")
st.subheader("Database Management")
with st.expander("Klik untuk melihat/hapus database lengkap"):
    st.dataframe(df_raw[COLUMNS], use_container_width=True)
    
    col_del1, col_del2 = st.columns([1, 4])
    with col_del1:
        id_hapus = st.number_input("Input ID (No)", min_value=1, step=1)
        if st.button("Hapus Baris"):
            db_mod = st.session_state["db"]
            db_mod = db_mod[db_mod["No"] != id_hapus]
            db_mod["No"] = range(1, len(db_mod) + 1)
            st.session_state["db"] = db_mod
            st.rerun()

# Download
st.markdown("---")
def to_excel(data):
    out = io.BytesIO()
    with pd.ExcelWriter(out, engine='openpyxl') as w:
        data[COLUMNS].to_excel(w, index=False)
    return out.getvalue()

st.download_button(
    label="Download Seluruh Rekap Gabungan (.xlsx)",
    data=to_excel(st.session_state["db"]),
    file_name=f"Quality_Gate_Rekap_{datetime.now().strftime('%Y%m%d')}.xlsx",
    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
)
