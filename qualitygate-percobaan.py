import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime
import io

# =====================================================
# PAGE CONFIG
# =====================================================
st.set_page_config(
    page_title="Quality Gate Monitoring",
    layout="wide",
    initial_sidebar_state="expanded"
)

# =====================================================
# CUSTOM CSS
# =====================================================
st.markdown("""
<style>

/* =========================
MAIN APP
========================= */
.stApp {
    background-color: #f1f4f9;
    font-family: 'Segoe UI', sans-serif;
}

/* =========================
MAIN CONTAINER
========================= */
.block-container {
    padding-top: 1rem;
    padding-left: 2rem;
    padding-right: 2rem;
    padding-bottom: 2rem;
}

/* =========================
SIDEBAR
========================= */
section[data-testid="stSidebar"] {
    background: linear-gradient(
        180deg,
        #081F5C 0%,
        #12337A 100%
    );
    border-right: 4px solid #8B0000;
}

/* Semua text sidebar */
section[data-testid="stSidebar"] * {
    color: white !important;
}

/* Label */
section[data-testid="stSidebar"] label {
    color: white !important;
    font-weight: 700 !important;
    font-size: 16px !important;
    opacity: 1 !important;
}

/* Input */
section[data-testid="stSidebar"] input,
section[data-testid="stSidebar"] textarea {
    background-color: rgba(255,255,255,0.18) !important;
    color: white !important;
    border-radius: 12px !important;
    border: 1px solid rgba(255,255,255,0.25) !important;
    font-weight: 600 !important;
}

/* Placeholder */
section[data-testid="stSidebar"] input::placeholder {
    color: rgba(255,255,255,0.8) !important;
}

/* Selectbox */
section[data-testid="stSidebar"] .stSelectbox div[data-baseweb="select"] > div {
    background-color: rgba(255,255,255,0.18) !important;
    border-radius: 12px !important;
    border: 1px solid rgba(255,255,255,0.25) !important;
    min-height: 48px !important;
}

/* Text selectbox */
section[data-testid="stSidebar"] .stSelectbox span {
    color: white !important;
    font-weight: 600 !important;
    opacity: 1 !important;
}

/* Date input */
section[data-testid="stSidebar"] .stDateInput input {
    background-color: rgba(255,255,255,0.18) !important;
    color: white !important;
    font-weight: 600 !important;
}

/* Form */
[data-testid="stForm"] {
    background: rgba(255,255,255,0.06);
    padding: 18px;
    border-radius: 18px;
    border: 1px solid rgba(255,255,255,0.12);
}

/* =========================
TITLE
========================= */
.dashboard-container {
    background: white;
    padding: 28px;
    border-radius: 22px;
    border-left: 10px solid #8B0000;
    box-shadow: 0 5px 18px rgba(0,0,0,0.08);
    margin-bottom: 25px;
}

.dashboard-title {
    font-size: 52px;
    font-weight: 900;
    color: #111111;
    letter-spacing: 1px;
    margin-bottom: 0;
}

/* =========================
SECTION TITLE
========================= */
.section-title {
    font-size: 26px;
    font-weight: 800;
    color: #081F5C;
    margin-top: 15px;
    margin-bottom: 18px;
}

/* =========================
KPI CARD
========================= */
.kpi-card {
    background: white;
    border-radius: 20px;
    padding: 24px;
    border-top: 6px solid #081F5C;
    box-shadow: 0 5px 15px rgba(0,0,0,0.08);
    text-align: center;
}

.kpi-title {
    font-size: 14px;
    font-weight: 700;
    color: #666;
    margin-bottom: 10px;
}

.kpi-value {
    font-size: 34px;
    font-weight: 900;
    color: #8B0000;
}

/* =========================
DATAFRAME
========================= */
[data-testid="stDataFrame"] {
    border-radius: 16px;
    overflow: hidden;
    border: 1px solid #d9d9d9;
    background: white;
}

/* =========================
CHART
========================= */
.stPlotlyChart {
    background: white;
    border-radius: 20px;
    padding: 14px;
    box-shadow: 0 5px 15px rgba(0,0,0,0.08);
}

/* =========================
BUTTON
========================= */
.stButton>button {
    background-color: #8B0000;
    color: white;
    border-radius: 10px;
    border: none;
    font-weight: 700;
    width: 100%;
    height: 45px;
}

.stDownloadButton>button {
    background-color: #081F5C;
    color: white;
    border-radius: 10px;
    border: none;
    font-weight: 700;
    width: 100%;
    height: 45px;
}

/* =========================
SUCCESS BOX
========================= */
.stSuccess {
    border-radius: 12px;
}

</style>
""", unsafe_allow_html=True)

# =====================================================
# HEADER
# =====================================================
st.markdown("""
<div class="dashboard-container">
    <div class="dashboard-title">
        QUALITY GATE MONITORING SYSTEM
    </div>
</div>
""", unsafe_allow_html=True)

# =====================================================
# COLUMN FORMAT
# =====================================================
COLUMNS = [
    "No",
    "Tanggal",
    "Shift",
    "No HP",
    "Layer HP",
    "Kode Mold",
    "No Lot",
    "Keterangan"
]

DEFECT_LIST = [
    "OK",
    "Visual",
    "Dimensi",
    "Visual Dimensi",
    "Dimensi Panjang",
    "Dimensi Lebar",
    "Dimensi Tebal",
    "Dimensi Panjang & Lebar",
    "Dimensi Panjang & Tebal",
    "Dimensi Lebar & Tebal"
]

# =====================================================
# SESSION STATE
# =====================================================
if "db" not in st.session_state:
    st.session_state["db"] = pd.DataFrame(columns=COLUMNS)

# =====================================================
# SIDEBAR
# =====================================================
st.sidebar.markdown("## DATA MANAGEMENT")

uploaded_file = st.sidebar.file_uploader(
    "Upload Excel",
    type=["xlsx"]
)

if uploaded_file:

    try:

        df_upload = pd.read_excel(uploaded_file)

        df_upload.columns = [
            str(c).strip()
            for c in df_upload.columns
        ]

        df_upload = df_upload.loc[
            :,
            ~df_upload.columns.duplicated()
        ]

        for col in COLUMNS:
            if col not in df_upload.columns:
                df_upload[col] = ""

        df_upload = df_upload[COLUMNS]

        df_upload["No"] = range(
            1,
            len(df_upload)+1
        )

        st.session_state["db"] = df_upload

        st.sidebar.success("Upload berhasil")

    except Exception as e:
        st.sidebar.error(f"Error : {e}")

# =====================================================
# INPUT FORM
# =====================================================
st.sidebar.markdown("## INPUT DATA")

with st.sidebar.form("form", clear_on_submit=True):

    tgl = st.date_input(
        "Tanggal",
        datetime.today(),
        format="DD/MM/YYYY"
    )

    shift = st.selectbox(
        "Shift",
        [1,2,3]
    )

    hp = st.selectbox(
        "No HP",
        [f"HP{i:02d}" for i in range(1,31)]
    )

    layer = st.selectbox(
        "Layer HP",
        [1,2,3,4,5]
    )

    mold = st.text_input("Kode Mold")

    lot = st.text_input("No Lot")

    ket = st.selectbox(
        "Keterangan",
        DEFECT_LIST
    )

    submit = st.form_submit_button(
        "Tambah Data"
    )

    if submit:

        df = st.session_state["db"].copy()

        new = pd.DataFrame([{
            "Tanggal": tgl.strftime("%d/%m/%Y"),
            "Shift": shift,
            "No HP": hp,
            "Layer HP": layer,
            "Kode Mold": mold,
            "No Lot": lot,
            "Keterangan": ket
        }])

        df = pd.concat(
            [
                df.drop(columns=["No"], errors="ignore"),
                new
            ],
            ignore_index=True
        )

        df["No"] = range(
            1,
            len(df)+1
        )

        st.session_state["db"] = df

        st.success("Data berhasil ditambahkan")

# =====================================================
# LOAD DATA
# =====================================================
df = st.session_state["db"].copy()

if df.empty:
    st.warning("Belum ada data")
    st.stop()

# =====================================================
# DATA CLEANING
# =====================================================
df["Tanggal"] = pd.to_datetime(
    df["Tanggal"],
    format="%d/%m/%Y",
    errors="coerce"
)

df["is_ng"] = (
    df["Keterangan"]
    .astype(str)
    .str.upper()
    .ne("OK")
    .astype(int)
)

df["is_ok"] = (
    df["Keterangan"]
    .astype(str)
    .str.upper()
    .eq("OK")
    .astype(int)
)

# =====================================================
# FILTER
# =====================================================
st.markdown(
    '<div class="section-title">FILTER DATA</div>',
    unsafe_allow_html=True
)

c1,c2,c3,c4 = st.columns(4)

with c1:

    f_shift = st.multiselect(
        "Shift",
        sorted(
            df["Shift"]
            .dropna()
            .unique()
        )
    )

with c2:

    f_hp = st.multiselect(
        "No HP",
        sorted(
            df["No HP"]
            .dropna()
            .unique()
        )
    )

with c3:

    f_ket = st.multiselect(
        "Keterangan",
        DEFECT_LIST
    )

with c4:

    f_date = st.date_input(
        "Tanggal Range",
        [],
        format="DD/MM/YYYY"
    )

df_f = df.copy()

if f_shift:
    df_f = df_f[
        df_f["Shift"].isin(f_shift)
    ]

if f_hp:
    df_f = df_f[
        df_f["No HP"].isin(f_hp)
    ]

if f_ket:
    df_f = df_f[
        df_f["Keterangan"].isin(f_ket)
    ]

if len(f_date) == 2:

    df_f = df_f[
        (
            df_f["Tanggal"] >= pd.to_datetime(f_date[0])
        )
        &
        (
            df_f["Tanggal"] <= pd.to_datetime(f_date[1])
        )
    ]

# =====================================================
# KPI
# =====================================================
jumlah_layer_jalan = len(df_f)

jumlah_layer_ok = int(
    df_f["is_ok"].sum()
)

jumlah_layer_ng = int(
    df_f["is_ng"].sum()
)

akurasi_ok = (
    jumlah_layer_ok /
    (jumlah_layer_ok + jumlah_layer_jalan)
    if (jumlah_layer_ok + jumlah_layer_jalan) > 0
    else 0
)

k1,k2,k3,k4 = st.columns(4)

with k1:
    st.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-title">JUMLAH LAYER JALAN</div>
        <div class="kpi-value">{jumlah_layer_jalan}</div>
    </div>
    """, unsafe_allow_html=True)

with k2:
    st.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-title">JUMLAH LAYER OK</div>
        <div class="kpi-value">{jumlah_layer_ok}</div>
    </div>
    """, unsafe_allow_html=True)

with k3:
    st.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-title">JUMLAH DEFECT</div>
        <div class="kpi-value">{jumlah_layer_ng}</div>
    </div>
    """, unsafe_allow_html=True)

with k4:
    st.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-title">AKURASI OK</div>
        <div class="kpi-value">{akurasi_ok:.2%}</div>
    </div>
    """, unsafe_allow_html=True)

# =====================================================
# TABEL JUMLAH DEFECT
# =====================================================
st.markdown(
    '<div class="section-title">JUMLAH DEFECT BERDASARKAN KATEGORI</div>',
    unsafe_allow_html=True
)

kategori_order = [
    "Dimensi",
    "Visual",
    "Visual Dimensi",
    "OK",
    "Dimensi Panjang",
    "Dimensi Lebar",
    "Dimensi Tebal",
    "Dimensi Panjang & Lebar",
    "Dimensi Panjang & Tebal",
    "Dimensi Lebar & Tebal"
]

kategori_df = (
    df_f["Keterangan"]
    .value_counts()
    .reindex(kategori_order, fill_value=0)
    .reset_index()
)

kategori_df.columns = [
    "Kategori Defect",
    "Jumlah"
]

kategori_df.index = range(
    1,
    len(kategori_df)+1
)

st.dataframe(
    kategori_df,
    width="stretch",
    height=420
)
