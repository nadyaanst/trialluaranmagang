import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import io

# Konfigurasi Halaman agar Dashboard Luas
st.set_page_config(
    page_title="Quality Gate Monitoring - Indoprima",
    layout="wide"
)

# Custom Styling (Inspirasi dari image_65de59.jpg)
st.markdown("""
    <style>
    .main { background-color: #f8f9fa; }
    .stMetric {
        background-color: #ffffff;
        padding: 20px;
        border-radius: 12px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        border-top: 5px solid #0056b3;
    }
    div[data-testid="stForm"] {
        border-radius: 15px;
        background-color: #ffffff;
        padding: 20px;
    }
    </style>
    """, unsafe_allow_html=True)

st.title("📊 Quality Gate Preforming Monitoring System")

# Definisi Kolom berdasarkan image_65da99.png
COLUMNS = ["No", "Tanggal", "Shift", "No HP", "Layer HP", "Kode Mold", "No Lot", "Keterangan"]
DEFECT_OPTIONS = [
    "OK", "Visual", "Dimensi", "Visual Dimensi", 
    "Dimensi Panjang", "Dimensi Lebar", "Dimensi Tebal", 
    "Dimensi Panjang & Lebar", "Dimensi Panjang & Tebal", "Dimensi Lebar & Tebal"
]

if "db" not in st.session_state:
    st.session_state["db"] = pd.DataFrame(columns=COLUMNS)

# --- SIDEBAR: MANAGEMENT & INPUT ---
st.sidebar.image("https://upload.wikimedia.org/wikipedia/commons/thumb/a/a0/Logo_Indoprima.png/250px-Logo_Indoprima.png", width=200) # Contoh placeholder logo
st.sidebar.header("📁 Data Management")

# Fitur Upload Excel (image_65da99.png)
uploaded_file = st.sidebar.file_uploader("Upload File Excel", type=["xlsx"])

if uploaded_file:
    try:
        df_upload = pd.read_excel(uploaded_file)
        df_upload.columns = [str(c).strip() for c in df_upload.columns]
        
        # Validasi kolom agar sesuai dengan image_65da99.png
        for col in COLUMNS:
            if col not in df_upload.columns:
                df_upload[col] = ""
        
        df_upload = df_upload[COLUMNS]
        df_upload["No"] = range(1, len(df_upload)+1)
        st.session_state["db"] = df_upload
        st.sidebar.success("✅ File berhasil dimuat!")
    except Exception as e:
        st.sidebar.error(f"Gagal memproses file: {e}")

st.sidebar.divider()
st.sidebar.header("📝 Input Manual")
with st.sidebar.form("form_input", clear_on_submit=True):
    t_tgl = st.date_input("Tanggal", datetime.today())
    t_shift = st.selectbox("Shift", [1, 2, 3])
    t_hp = st.selectbox("No HP", [f"HP{i:02d}" for i in range(1, 31)])
    t_layer = st.selectbox("Layer HP", [1, 2, 3, 4, 5])
    t_mold = st.text_input("Kode Mold")
    t_lot = st.text_input("No Lot")
    t_ket = st.selectbox("Keterangan", DEFECT_OPTIONS)
    
    if st.form_submit_button("Tambah ke Database"):
        df_new = pd.DataFrame([{
            "Tanggal": t_tgl.strftime("%d/%m/%Y"),
            "Shift": t_shift, "No HP": t_hp, "Layer HP": t_layer,
            "Kode Mold": t_mold, "No Lot": t_lot, "Keterangan": t_ket
        }])
        current_db = st.session_state["db"].copy()
        updated_db = pd.concat([current_db.drop(columns=["No"], errors="ignore"), df_new], ignore_index=True)
        updated_db["No"] = range(1, len(updated_db)+1)
        st.session_state["db"] = updated_db
        st.success("Data berhasil ditambahkan!")

# --- MAIN DASHBOARD ---
df_master = st.session_state["db"].copy()

if df_master.empty:
    st.info("Silakan unggah file Excel atau masukkan data manual untuk melihat statistik.")
    st.stop()

# Konversi Tanggal untuk perhitungan
df_master["Tanggal_DT"] = pd.to_datetime(df_master["Tanggal"], dayfirst=True, errors="coerce")
df_master["is_ng"] = df_master["Keterangan"].astype(str).str.upper().ne("OK").astype(int)
df_master["is_ok"] = df_master["Keterangan"].astype(str).str.upper().eq("OK").astype(int)

# --- FILTER DATA SECTION (image_65da75.png) ---
st.subheader("🔍 Filter Data")
f1, f2, f3, f4 = st.columns(4)

with f1:
    f_shift = st.multiselect("Shift", sorted(df_master["Shift"].unique()))
with f2:
    f_hp = st.multiselect("No HP", sorted(df_master["No HP"].unique()))
with f3:
    f_ket = st.multiselect("Keterangan", DEFECT_OPTIONS)
with f4:
    f_range = st.date_input("Tanggal Range", [])

# Logika Filter
df_f = df_master.copy()
if f_shift: df_f = df_f[df_f["Shift"].isin(f_shift)]
if f_hp: df_f = df_f[df_f["No HP"].isin(f_hp)]
if f_ket: df_f = df_f[df_f["Keterangan"].isin(f_ket)]
if len(f_range) == 2:
    df_f = df_f[(df_f["Tanggal_DT"] >= pd.to_datetime(f_range[0])) & 
                (df_f["Tanggal_DT"] <= pd.to_datetime(f_range[1]))]

# --- SCORECARDS ---
total_jalan = len(df_f)
total_ok = int(df_f["is_ok"].sum())
akurasi = total_ok / total_jalan if total_jalan > 0 else 0

m1, m2, m3 = st.columns(3)
m1.metric("Jumlah Layer Jalan", f"{total_jalan} pcs")
m2.metric("Jumlah Layer OK", f"{total_ok} pcs")
m3.metric("Akurasi OK", f"{akurasi:.2%}")

# --- COMBO CHART ---
st.subheader("📈 Analisis Tren Harian")
daily = df_f.groupby(df_f["Tanggal_DT"].dt.date).agg(
    total_jalan=('No', 'count'),
    total_ok=('is_ok', 'sum')
).reset_index()
daily["akurasi"] = (daily["total_ok"] / daily["total_jalan"]) * 100

fig = go.Figure()
fig.add_trace(go.Bar(x=daily["Tanggal_DT"], y=daily["total_jalan"], name="Total Jalan", marker_color='#0056b3'))
fig.add_trace(go.Scatter(x=daily["Tanggal_DT"], y=daily["akurasi"], name="Akurasi (%)", yaxis="y2", line=dict(color='#d32f2f', width=3)))

fig.update_layout(
    yaxis=dict(title="Volume Produksi"),
    yaxis2=dict(title="Akurasi (%)", overlaying="y", side="right", range=[0, 105]),
    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
)
st.plotly_chart(fig, use_container_width=True)

# --- TOP 5 SECTION ---
c_top1, c_top2 = st.columns(2)

with c_top1:
    st.subheader("🔥 Top 5 Mesin Hotpress (NG)")
    top_hp = df_f.groupby("No HP")["is_ng"].sum().reset_index().sort_values("is_ng", ascending=False).head(5)
    st.dataframe(top_hp.rename(columns={"is_ng": "Jumlah NG"}), use_container_width=True)

with c_top2:
    st.subheader("🏗️ Top 5 Molding (NG)")
    top_mold = df_f.groupby("Kode Mold")["is_ng"].sum().reset_index().sort_values("is_ng", ascending=False).head(5)
    st.dataframe(top_mold.rename(columns={"is_ng": "Jumlah NG"}), use_container_width=True)

# --- DATA TABLE & EXPORT ---
st.subheader("📋 Detail Data Terfilter")
st.dataframe(df_f[COLUMNS], use_container_width=True)

# Tombol Download
excel_file = io.BytesIO()
with pd.ExcelWriter(excel_file, engine='openpyxl') as writer:
    df_f[COLUMNS].to_excel(writer, index=False)
st.download_button(
    label="📥 Download Data ke Excel",
    data=excel_file.getvalue(),
    file_name=f"Report_Quality_{datetime.now().strftime('%Y%m%d')}.xlsx"
)
