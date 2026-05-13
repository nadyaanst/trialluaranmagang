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

@import url('https://fonts.googleapis.com/css2?family=Oswald:wght@400;500;600;700&family=Inter:wght@400;500;600;700&display=swap');

html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
    background-color: #eef2f7;
}

/* MAIN AREA */
.main {
    background-color: #eef2f7;
}

.block-container {
    padding-top: 1rem;
    padding-bottom: 2rem;
    max-width: 95%;
}

/* SIDEBAR */
section[data-testid="stSidebar"] {
    background: linear-gradient(
        180deg,
        #0b1f4d 0%,
        #132f73 100%
    );
    border-right: 4px solid #991b1b;
}

section[data-testid="stSidebar"] * {
    color: white !important;
}

/* HEADER */
.dashboard-header {
    background: white;
    padding: 30px 40px;
    border-radius: 22px;
    border-left: 10px solid #991b1b;
    box-shadow: 0 4px 18px rgba(0,0,0,0.08);
    margin-bottom: 25px;
}

.dashboard-title {
    font-family: 'Oswald', sans-serif;
    font-size: 48px;
    font-weight: 700;
    color: #111827;
    letter-spacing: 1px;
}

.dashboard-subtitle {
    margin-top: 10px;
    font-size: 16px;
    color: #6b7280;
    font-weight: 500;
}

/* SECTION TITLE */
.section-title {
    font-family: 'Oswald', sans-serif;
    font-size: 28px;
    color: #111827;
    margin-top: 20px;
    margin-bottom: 15px;
    letter-spacing: 0.5px;
}

/* KPI CARD */
.kpi-card {
    background: linear-gradient(
        135deg,
        #0f172a 0%,
        #1e3a8a 100%
    );
    padding: 24px;
    border-radius: 20px;
    border-top: 5px solid #991b1b;
    box-shadow: 0 6px 18px rgba(0,0,0,0.10);
    color: white;
    margin-bottom: 10px;
}

.kpi-title {
    font-size: 15px;
    font-weight: 600;
    color: #dbeafe;
    margin-bottom: 12px;
}

.kpi-value {
    font-size: 38px;
    font-weight: 700;
    color: white;
}

/* CHART */
.stPlotlyChart {
    background: white;
    padding: 15px;
    border-radius: 22px;
    border-top: 5px solid #991b1b;
    box-shadow: 0 4px 16px rgba(0,0,0,0.06);
}

/* TABLE */
[data-testid="stDataFrame"] {
    background: white;
    border-radius: 22px;
    padding: 12px;
    border-top: 5px solid #991b1b;
    box-shadow: 0 4px 16px rgba(0,0,0,0.06);
}

/* BUTTON */
.stButton>button {
    background: #991b1b;
    color: white;
    border: none;
    border-radius: 12px;
    font-weight: 600;
}

.stDownloadButton>button {
    background: #0b1f4d;
    color: white;
    border: none;
    border-radius: 12px;
    font-weight: 600;
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

    submit = st.form_submit_button("Tambah Data")

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

c1, c2, c3, c4 = st.columns(4)

with c1:

    f_shift = st.multiselect(
        "Shift",
        sorted(df["Shift"].dropna().unique())
    )

with c2:

    f_hp = st.multiselect(
        "No HP",
        sorted(df["No HP"].dropna().unique())
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
    df_f = df_f[df_f["Shift"].isin(f_shift)]

if f_hp:
    df_f = df_f[df_f["No HP"].isin(f_hp)]

if f_ket:
    df_f = df_f[df_f["Keterangan"].isin(f_ket)]

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

jumlah_layer_ok = int(df_f["is_ok"].sum())

jumlah_layer_ng = int(df_f["is_ng"].sum())

akurasi_ok = (
    jumlah_layer_ok /
    jumlah_layer_jalan
    if jumlah_layer_jalan > 0
    else 0
)

st.markdown(
    '<div class="section-title">PERFORMANCE OVERVIEW</div>',
    unsafe_allow_html=True
)

k1, k2, k3, k4 = st.columns(4)

with k1:
    st.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-title">
            JUMLAH LAYER JALAN
        </div>

        <div class="kpi-value">
            {jumlah_layer_jalan}
        </div>
    </div>
    """, unsafe_allow_html=True)

with k2:
    st.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-title">
            JUMLAH LAYER OK
        </div>

        <div class="kpi-value">
            {jumlah_layer_ok}
        </div>
    </div>
    """, unsafe_allow_html=True)

with k3:
    st.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-title">
            JUMLAH LAYER NG
        </div>

        <div class="kpi-value">
            {jumlah_layer_ng}
        </div>
    </div>
    """, unsafe_allow_html=True)

with k4:
    st.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-title">
            AKURASI OK
        </div>

        <div class="kpi-value">
            {akurasi_ok:.2%}
        </div>
    </div>
    """, unsafe_allow_html=True)

# =====================================================
# COMBO CHART
# =====================================================

st.markdown(
    '<div class="section-title">MONITORING HARIAN</div>',
    unsafe_allow_html=True
)

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
        marker_color="#1e3a8a"
    ),
    secondary_y=False
)

fig_combo.add_trace(
    go.Scatter(
        x=daily["Tanggal"],
        y=daily["Akurasi"],
        mode="lines+markers",
        name="Akurasi OK",
        line=dict(color="#991b1b", width=4)
    ),
    secondary_y=True
)

fig_combo.update_layout(
    template="plotly_white",
    height=500,
    hovermode="x unified"
)

fig_combo.update_yaxes(
    title_text="Jumlah Layer",
    secondary_y=False
)

fig_combo.update_yaxes(
    title_text="Akurasi",
    tickformat=".0%",
    secondary_y=True
)

st.plotly_chart(
    fig_combo,
    width="stretch"
)

# =====================================================
# TOP TABLE
# =====================================================

t1, t2 = st.columns(2)

with t1:

    st.markdown(
        '<div class="section-title">TOP 5 MESIN HOTPRESS BERMASALAH</div>',
        unsafe_allow_html=True
    )

    top_hp = (
        df_f.groupby("No HP")["is_ng"]
        .sum()
        .reset_index()
        .rename(columns={
            "No HP":"Mesin Hotpress",
            "is_ng":"Jumlah Defect"
        })
        .sort_values(
            by="Jumlah Defect",
            ascending=False
        )
        .head(5)
    )

    st.dataframe(
        top_hp,
        width="stretch",
        height=250
    )

with t2:

    st.markdown(
        '<div class="section-title">TOP 5 MOLDING BERMASALAH</div>',
        unsafe_allow_html=True
    )

    top_mold = (
        df_f.groupby("Kode Mold")["is_ng"]
        .sum()
        .reset_index()
        .rename(columns={
            "Kode Mold":"Kode Mold",
            "is_ng":"Jumlah Defect"
        })
        .sort_values(
            by="Jumlah Defect",
            ascending=False
        )
        .head(5)
    )

    st.dataframe(
        top_mold,
        width="stretch",
        height=250
    )

# =====================================================
# ANALYSIS
# =====================================================

st.markdown(
    '<div class="section-title">ANALISIS DATA</div>',
    unsafe_allow_html=True
)

g1, g2 = st.columns(2)

with g1:

    mesin = (
        df_f.groupby("No HP")["is_ng"]
        .sum()
        .reset_index()
    )

    fig1 = px.bar(
        mesin,
        x="No HP",
        y="is_ng",
        title="Jumlah Defect per Mesin",
        text_auto=True
    )

    fig1.update_layout(
        template="plotly_white",
        height=450
    )

    st.plotly_chart(
        fig1,
        width="stretch"
    )

with g2:

    cacat = (
        df_f[df_f["is_ng"] == 1]
        ["Keterangan"]
        .value_counts()
        .reset_index()
    )

    cacat.columns = [
        "Jenis Defect",
        "Jumlah"
    ]

    fig2 = px.pie(
        cacat,
        names="Jenis Defect",
        values="Jumlah",
        hole=0.5
    )

    fig2.update_layout(
        template="plotly_white",
        height=450
    )

    st.plotly_chart(
        fig2,
        width="stretch"
    )

# =====================================================
# TABLE DATA
# =====================================================

st.markdown(
    '<div class="section-title">TABEL DATA</div>',
    unsafe_allow_html=True
)

df_show = df_f.copy()

df_show["Tanggal"] = (
    df_show["Tanggal"]
    .dt.strftime("%d/%m/%Y")
)

st.dataframe(
    df_show[COLUMNS],
    width="stretch",
    height=450
)

# =====================================================
# DELETE DATA
# =====================================================

st.markdown(
    '<div class="section-title">HAPUS DATA</div>',
    unsafe_allow_html=True
)

hapus = st.number_input(
    "Masukkan Nomor Data",
    min_value=1,
    step=1
)

if st.button("Hapus"):

    df = st.session_state["db"]

    df = df[
        df["No"] != hapus
    ]

    df["No"] = range(
        1,
        len(df)+1
    )

    st.session_state["db"] = df

    st.success("Data berhasil dihapus")

# =====================================================
# DOWNLOAD
# =====================================================

st.markdown(
    '<div class="section-title">DOWNLOAD DATA</div>',
    unsafe_allow_html=True
)

def convert_excel(data):

    export = data.copy()

    if "Tanggal" in export.columns:

        export["Tanggal"] = pd.to_datetime(
            export["Tanggal"],
            errors="coerce"
        ).dt.strftime("%d/%m/%Y")

    output = io.BytesIO()

    with pd.ExcelWriter(
        output,
        engine="openpyxl"
    ) as writer:

        export[COLUMNS].to_excel(
            writer,
            index=False
        )

    return output.getvalue()

st.download_button(
    label="Download Excel",
    data=convert_excel(df),
    file_name="quality_gate.xlsx"
)
