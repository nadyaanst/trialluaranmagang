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

section[data-testid="stSidebar"] * {
    color: white !important;
}

section[data-testid="stSidebar"] label {
    color: white !important;
    font-weight: 600;
}

section[data-testid="stSidebar"] .stTextInput input,
section[data-testid="stSidebar"] .stSelectbox div,
section[data-testid="stSidebar"] .stDateInput input {
    background-color: rgba(255,255,255,0.12);
    border-radius: 10px;
    color: white !important;
    border: 1px solid rgba(255,255,255,0.15);
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

/* =========================
INPUT FORM BOX
========================= */
[data-testid="stForm"] {
    background: rgba(255,255,255,0.05);
    padding: 18px;
    border-radius: 18px;
    border: 1px solid rgba(255,255,255,0.1);
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

persentase_ok = (
    jumlah_layer_ok /
    jumlah_layer_jalan
    if jumlah_layer_jalan > 0
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
        <div class="kpi-title">PERSENTASE OK</div>
        <div class="kpi-value">{persentase_ok:.2%}</div>
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
    .sort_values("Tanggal")
)

daily.columns = [
    "Tanggal",
    "Layer Jalan",
    "Layer OK"
]

daily["Persentase OK"] = (
    daily["Layer OK"] /
    daily["Layer Jalan"]
)

daily["Target"] = 1

fig_combo = make_subplots(
    specs=[[{"secondary_y": True}]]
)

# BAR LAYER JALAN
fig_combo.add_trace(

    go.Bar(
        x=daily["Tanggal"],
        y=daily["Layer Jalan"],
        name="Total Layer Jalan",
        marker_color="#8B0000",
        text=daily["Layer Jalan"],
        textposition="outside",
        textfont=dict(
            color="black",
            size=12
        )
    ),

    secondary_y=False
)

# BAR LAYER OK
fig_combo.add_trace(

    go.Bar(
        x=daily["Tanggal"],
        y=daily["Layer OK"],
        name="Total Layer OK",
        marker_color="#081F5C",
        text=daily["Layer OK"],
        textposition="outside",
        textfont=dict(
            color="black",
            size=12
        )
    ),

    secondary_y=False
)

# LINE PERSENTASE OK
fig_combo.add_trace(

    go.Scatter(
        x=daily["Tanggal"],
        y=daily["Persentase OK"],
        mode="lines+markers+text",
        name="Persentase OK",
        line=dict(
            color="#FF6B00",
            width=4
        ),
        marker=dict(
            size=10,
            color="#FF6B00"
        ),
        text=[
            f"{x:.1%}"
            for x in daily["Persentase OK"]
        ],
        textposition="top center",
        textfont=dict(
            color="black",
            size=12
        )
    ),

    secondary_y=True
)

# TARGET
fig_combo.add_trace(

    go.Scatter(
        x=daily["Tanggal"],
        y=daily["Target"],
        mode="lines",
        name="Target 100%",
        line=dict(
            color="#00C853",
            width=3,
            dash="dash"
        )
    ),

    secondary_y=True
)

fig_combo.update_layout(

    height=560,

    template="plotly_white",

    hovermode="x unified",

    barmode="group",

    plot_bgcolor="white",
    paper_bgcolor="white",

    font=dict(
        family="Segoe UI",
        size=13,
        color="black"
    ),

    legend=dict(
        orientation="h",
        yanchor="bottom",
        y=1.02,
        xanchor="center",
        x=0.5,
        font=dict(color="black")
    ),

    xaxis=dict(
        rangeslider=dict(
            visible=True
        ),
        type="date",
        range=[
            daily["Tanggal"].min(),
            daily["Tanggal"].min() + pd.Timedelta(days=6)
        ],
        title_font=dict(color="black"),
        tickfont=dict(color="black")
    )
)

fig_combo.update_yaxes(
    title_text="Jumlah Layer",
    secondary_y=False,
    title_font=dict(color="black"),
    tickfont=dict(color="black"),
    gridcolor="rgba(0,0,0,0.08)"
)

fig_combo.update_yaxes(
    title_text="Persentase OK",
    tickformat=".0%",
    range=[0,1.1],
    secondary_y=True,
    title_font=dict(color="black"),
    tickfont=dict(color="black")
)

st.plotly_chart(
    fig_combo,
    width="stretch"
)

# =====================================================
# ANALISIS DATA
# =====================================================
st.markdown(
    '<div class="section-title">ANALISIS DATA</div>',
    unsafe_allow_html=True
)

g1,g2 = st.columns(2)

# =====================================================
# GRAFIK MESIN
# =====================================================
with g1:

    mesin = (
        df_f.groupby("No HP")["is_ng"]
        .sum()
        .reset_index()
        .rename(columns={
            "is_ng":"Jumlah Defect"
        })
    )

    fig1 = px.bar(
        mesin,
        x="No HP",
        y="Jumlah Defect",
        text="Jumlah Defect"
    )

    fig1.update_traces(
        marker_color="#0B1F4D",
        textposition="outside",
        textfont=dict(
            color="black",
            size=12
        )
    )

    fig1.update_layout(
        title="Jumlah Defect per Mesin",
        template="plotly_white",
        height=420,
        xaxis_title="No HP",
        yaxis_title="Jumlah Defect",

        font=dict(
            color="black"
        ),

        xaxis=dict(
            title_font=dict(color="black"),
            tickfont=dict(color="black")
        ),

        yaxis=dict(
            title_font=dict(color="black"),
            tickfont=dict(color="black")
        )
    )

    st.plotly_chart(
        fig1,
        width="stretch"
    )

# =====================================================
# PIE CHART
# =====================================================
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
        hole=0.45
    )

    fig2.update_traces(
        textfont=dict(
            color="black",
            size=12
        ),
        textinfo="percent+label"
    )

    fig2.update_layout(
        title="Distribusi Jenis Defect",
        template="plotly_white",
        height=420,

        font=dict(
            color="black"
        ),

        legend=dict(
            font=dict(color="black")
        )
    )

    st.plotly_chart(
        fig2,
        width="stretch"
    )

# =====================================================
# VISUALISASI DEFECT MOLDING
# =====================================================
st.markdown(
    '<div class="section-title">VISUALISASI DEFECT MOLDING</div>',
    unsafe_allow_html=True
)

mold_chart = (
    df_f.groupby("Kode Mold")["is_ng"]
    .sum()
    .reset_index()
    .rename(columns={
        "is_ng":"Jumlah Defect"
    })
    .sort_values(
        by="Jumlah Defect",
        ascending=False
    )
    .head(10)
)

fig_mold = go.Figure()

fig_mold.add_trace(

    go.Bar(
        x=mold_chart["Kode Mold"],
        y=mold_chart["Jumlah Defect"],
        text=mold_chart["Jumlah Defect"],
        textposition="outside",
        textfont=dict(
            color="black",
            size=12
        ),
        marker_color="#8B0000",
        name="Jumlah Defect"
    )
)

fig_mold.update_layout(

    title={
        "text":"Top 10 Defect Molding",
        "x":0.5
    },

    template="plotly_white",

    height=500,

    plot_bgcolor="white",
    paper_bgcolor="white",

    xaxis_title="Kode Mold",
    yaxis_title="Jumlah Defect",

    font=dict(
        color="black"
    ),

    xaxis=dict(
        title_font=dict(color="black"),
        tickfont=dict(color="black")
    ),

    yaxis=dict(
        title_font=dict(color="black"),
        tickfont=dict(color="black")
    )
)

st.plotly_chart(
    fig_mold,
    width="stretch"
)
