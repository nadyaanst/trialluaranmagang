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
FONT
========================= */

@import url('https://fonts.googleapis.com/css2?family=Barlow:wght@400;500;600;700;800&display=swap');

html, body, [class*="css"] {
    font-family: 'Barlow', sans-serif;
}

/* =========================
MAIN BACKGROUND
========================= */

.main {
    background-color: #f3f5fa;
}

.block-container {
    padding-top: 1rem;
    padding-bottom: 1rem;
    max-width: 100%;
}

/* =========================
HEADER
========================= */

.dashboard-header {
    background: white;
    padding: 24px 32px;
    border-radius: 18px;
    border-left: 10px solid #c1121f;
    box-shadow: 0 4px 20px rgba(0,0,0,0.08);
    margin-bottom: 20px;
}

.dashboard-title {
    font-size: 38px;
    font-weight: 800;
    color: #111111;
    letter-spacing: 1px;
    line-height: 1.1;
}

.dashboard-subtitle {
    font-size: 16px;
    color: #6b7280;
    font-weight: 500;
    margin-top: 8px;
}

/* =========================
SIDEBAR
========================= */

section[data-testid="stSidebar"] {
    background: linear-gradient(
        180deg,
        #1d2f6f 0%,
        #243b8a 100%
    );
}

section[data-testid="stSidebar"] * {
    color: white !important;
    font-family: 'Barlow', sans-serif;
}

section[data-testid="stSidebar"] label {
    font-weight: 700 !important;
}

/* =========================
SECTION TITLE
========================= */

.section-title {
    font-size: 24px;
    font-weight: 800;
    color: #1d2f6f;
    margin-top: 12px;
    margin-bottom: 14px;
    text-transform: uppercase;
}

/* =========================
KPI CARD
========================= */

.kpi-card {
    background: white;
    border-radius: 18px;
    padding: 24px;
    text-align: center;
    box-shadow: 0 4px 18px rgba(0,0,0,0.08);
    border-top: 8px solid #1d2f6f;
}

.kpi-card-red {
    border-top: 8px solid #c1121f;
}

.kpi-title {
    font-size: 14px;
    font-weight: 700;
    color: #6b7280;
    text-transform: uppercase;
    margin-bottom: 12px;
    letter-spacing: 0.5px;
}

.kpi-value {
    font-size: 38px;
    font-weight: 800;
    color: #111111;
}

/* =========================
CARD
========================= */

.card {
    background: white;
    border-radius: 18px;
    padding: 16px;
    box-shadow: 0 4px 18px rgba(0,0,0,0.08);
    margin-bottom: 10px;
}

.card-title {
    font-size: 18px;
    font-weight: 800;
    color: #1d2f6f;
    text-transform: uppercase;
}

/* =========================
TABLE
========================= */

[data-testid="stDataFrame"] {
    border-radius: 18px;
    overflow: hidden;
    border: 1px solid #e5e7eb;
    background: white;
}

/* =========================
CHART
========================= */

.stPlotlyChart {
    background: white;
    border-radius: 18px;
    padding: 10px;
    box-shadow: 0 4px 18px rgba(0,0,0,0.08);
}

/* =========================
BUTTON
========================= */

.stButton > button {
    width: 100%;
    background-color: #c1121f;
    color: white;
    border: none;
    border-radius: 10px;
    height: 45px;
    font-weight: 700;
}

.stButton > button:hover {
    background-color: #980c17;
    color: white;
}

.stDownloadButton > button {
    width: 100%;
    background-color: #1d2f6f;
    color: white;
    border: none;
    border-radius: 10px;
    height: 45px;
    font-weight: 700;
}

.stDownloadButton > button:hover {
    background-color: #162452;
    color: white;
}

</style>
""", unsafe_allow_html=True)

# =====================================================
# HEADER
# =====================================================

st.markdown("""
<div class="dashboard-header">
    <div class="dashboard-title">
        QUALITY GATE MONITORING SYSTEM
    </div>

    <div class="dashboard-subtitle">
        Internal Quality Monitoring Dashboard
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

st.sidebar.header("DATA MANAGEMENT")

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

st.sidebar.header("INPUT DATA")

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

st.markdown("""
<div class="section-title">
Filter Data
</div>
""", unsafe_allow_html=True)

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
    (jumlah_layer_ok + jumlah_layer_ng)
    if (jumlah_layer_ok + jumlah_layer_ng) > 0
    else 0
)

st.markdown("""
<div class="section-title">
Performance Overview
</div>
""", unsafe_allow_html=True)

k1,k2,k3,k4 = st.columns(4)

with k1:

    st.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-title">
            Jumlah Layer Jalan
        </div>

        <div class="kpi-value">
            {jumlah_layer_jalan:,}
        </div>
    </div>
    """, unsafe_allow_html=True)

with k2:

    st.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-title">
            Jumlah Layer OK
        </div>

        <div class="kpi-value">
            {jumlah_layer_ok:,}
        </div>
    </div>
    """, unsafe_allow_html=True)

with k3:

    st.markdown(f"""
    <div class="kpi-card kpi-card-red">
        <div class="kpi-title">
            Jumlah Layer NG
        </div>

        <div class="kpi-value">
            {jumlah_layer_ng:,}
        </div>
    </div>
    """, unsafe_allow_html=True)

with k4:

    st.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-title">
            Akurasi OK
        </div>

        <div class="kpi-value">
            {akurasi_ok:.2%}
        </div>
    </div>
    """, unsafe_allow_html=True)

# =====================================================
# COMBO CHART
# =====================================================

st.markdown("""
<div class="section-title">
Trend Harian Layer dan Akurasi
</div>
""", unsafe_allow_html=True)

daily = (
    df_f.groupby("Tanggal")
    .agg({
        "Layer HP":"count",
        "is_ok":"sum"
    })
    .reset_index()
)

daily.columns = [
    "Tanggal",
    "Layer Jalan",
    "Layer OK"
]

daily["Akurasi"] = (
    daily["Layer OK"] /
    daily["Layer Jalan"]
)

fig_combo = make_subplots(
    specs=[[{"secondary_y": True}]]
)

fig_combo.add_trace(

    go.Bar(
        x=daily["Tanggal"],
        y=daily["Layer Jalan"],
        name="Jumlah Layer Jalan",
        marker_color="#1d2f6f"
    ),

    secondary_y=False
)

fig_combo.add_trace(

    go.Scatter(
        x=daily["Tanggal"],
        y=daily["Akurasi"],
        mode="lines+markers",
        name="Akurasi OK",
        line=dict(
            color="#c1121f",
            width=4
        )
    ),

    secondary_y=True
)

fig_combo.update_layout(
    paper_bgcolor="white",
    plot_bgcolor="white",

    font=dict(
        family="Barlow",
        size=13,
        color="#111111"
    ),

    legend=dict(
        orientation="h",
        y=1.08
    ),

    hovermode="x unified",
    height=500
)

fig_combo.update_yaxes(
    title_text="Jumlah Layer",
    secondary_y=False,
    gridcolor="#e5e7eb"
)

fig_combo.update_yaxes(
    title_text="Akurasi",
    tickformat=".0%",
    secondary_y=True,
    gridcolor="#e5e7eb"
)

st.plotly_chart(
    fig_combo,
    width="stretch"
)
