# =====================================================
# IMPORT LIBRARY
# =====================================================
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime
import io
from streamlit_plotly_events import plotly_events

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
# COLUMN
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

df["Kode Mold"] = (
    df["Kode Mold"]
    .astype(str)
    .str.strip()
    .str.upper()
)

df["Keterangan"] = (
    df["Keterangan"]
    .astype(str)
    .str.strip()
)

df["is_ng"] = (
    df["Keterangan"]
    .str.upper()
    .ne("OK")
    .astype(int)
)

df["is_ok"] = (
    df["Keterangan"]
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
# VISUALISASI DEFECT MOLDING
# =====================================================
st.markdown(
    '<div class="section-title">VISUALISASI DEFECT MOLDING</div>',
    unsafe_allow_html=True
)

# =====================================================
# DATA KHUSUS DEFECT
# =====================================================

mold_chart = (
    df_f[df_f["is_ng"] == 1]
    .groupby("Kode Mold")
    .size()
    .reset_index(name="Jumlah Defect")
)

# HAPUS KOSONG
mold_chart = mold_chart[
    mold_chart["Kode Mold"] != ""
]

# SORTING
mold_chart = mold_chart.sort_values(
    by="Jumlah Defect",
    ascending=False
).head(10)

# RESET INDEX
mold_chart = mold_chart.reset_index(drop=True)

# =====================================================
# VERTICAL BAR CHART
# =====================================================

fig_mold = go.Figure()

fig_mold.add_trace(

    go.Bar(

        x=mold_chart["Kode Mold"],
        y=mold_chart["Jumlah Defect"],

        text=mold_chart["Jumlah Defect"],
        textposition="outside",

        marker=dict(
            color="#8B0000",
            line=dict(
                color="#5c0000",
                width=1.5
            )
        ),

        width=0.6,

        hovertemplate=
        "<b>Kode Mold :</b> %{x}<br>" +
        "<b>Jumlah Defect :</b> %{y}<extra></extra>"
    )
)

fig_mold.update_layout(

    template="plotly_white",

    height=550,

    title=dict(
        text="TOP 10 DEFECT MOLDING",
        x=0.5,
        font=dict(
            size=24,
            color="#081F5C"
        )
    ),

    plot_bgcolor="white",
    paper_bgcolor="white",

    font=dict(
        family="Segoe UI",
        size=13,
        color="black"
    ),

    margin=dict(
        l=50,
        r=30,
        t=80,
        b=80
    ),

    xaxis=dict(
        title="Kode Mold",
        tickangle=-35,
        showgrid=False,
        categoryorder="total descending"
    ),

    yaxis=dict(
        title="Jumlah Defect",
        gridcolor="rgba(0,0,0,0.08)"
    )
)

# =====================================================
# SHOW CHART
# =====================================================

selected_points = plotly_events(
    fig_mold,
    click_event=True,
    hover_event=False,
    select_event=False,
    override_height=550,
    key="mold_chart"
)

# =====================================================
# DETAIL KETIKA BAR DIKLIK
# =====================================================

if selected_points:

    # =====================================================
    # AMBIL KODE MOLD LANGSUNG DARI X
    # =====================================================

    selected_mold = selected_points[0]["x"]

    # =====================================================
    # FILTER DETAIL SESUAI MOLD
    # =====================================================

    detail_df = df_f[
        df_f["Kode Mold"] == selected_mold
    ].copy()

    detail_df["Tanggal"] = (
        detail_df["Tanggal"]
        .dt.strftime("%d/%m/%Y")
    )

    # =====================================================
    # HEADER
    # =====================================================

    st.markdown(f"""
    <div style="
        background:white;
        padding:22px;
        border-radius:18px;
        border-left:8px solid #8B0000;
        box-shadow:0 4px 12px rgba(0,0,0,0.08);
        margin-top:25px;
        margin-bottom:20px;
    ">
        <div style="
            font-size:28px;
            font-weight:800;
            color:#081F5C;
        ">
            DETAIL MOLD : {selected_mold}
        </div>
    </div>
    """, unsafe_allow_html=True)

    # =====================================================
    # KPI DETAIL
    # =====================================================

    total_data = len(detail_df)

    total_ok = int(detail_df["is_ok"].sum())

    total_ng = int(detail_df["is_ng"].sum())

    d1,d2,d3 = st.columns(3)

    with d1:
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-title">TOTAL DATA</div>
            <div class="kpi-value">{total_data}</div>
        </div>
        """, unsafe_allow_html=True)

    with d2:
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-title">TOTAL OK</div>
            <div class="kpi-value">{total_ok}</div>
        </div>
        """, unsafe_allow_html=True)

    with d3:
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-title">TOTAL DEFECT</div>
            <div class="kpi-value">{total_ng}</div>
        </div>
        """, unsafe_allow_html=True)

    # =====================================================
    # REKAP PER TANGGAL
    # =====================================================

    st.markdown("## REKAP DEFECT")

    rekap = (
        detail_df.groupby(
            ["Tanggal", "Keterangan"]
        )
        .size()
        .reset_index(name="Jumlah PCS")
    )

    tanggal_unik = rekap["Tanggal"].unique()

    for tgl in tanggal_unik:

        sub = rekap[
            rekap["Tanggal"] == tgl
        ]

        st.markdown(f"### 📅 {tgl}")

        st.dataframe(
            sub.rename(columns={
                "Keterangan":"Jenis Defect"
            }),
            width="stretch",
            hide_index=True
        )

    # =====================================================
    # DETAIL DATA
    # =====================================================

    st.markdown("## DETAIL DATA")

    st.dataframe(
        detail_df[
            [
                "Tanggal",
                "Shift",
                "No HP",
                "Layer HP",
                "No Lot",
                "Keterangan"
            ]
        ],
        width="stretch",
        height=350,
        hide_index=True
    )

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
