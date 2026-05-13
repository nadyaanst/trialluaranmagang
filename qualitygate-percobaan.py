import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime
import io

st.set_page_config(
    page_title="Quality Gate Monitoring",
    layout="wide",
    initial_sidebar_state="expanded"
)

# =========================
# CUSTOM CSS
# =========================
st.markdown("""
<style>

.main {
    background-color: #f5f7fb;
}

.block-container {
    padding-top: 1rem;
    padding-bottom: 2rem;
}

h1, h2, h3 {
    font-weight: 700;
}

[data-testid="stMetric"] {
    background: white;
    padding: 18px;
    border-radius: 18px;
    border: 1px solid #eaeaea;
    box-shadow: 0 2px 10px rgba(0,0,0,0.04);
}

[data-testid="stDataFrame"] {
    background: white;
    border-radius: 18px;
    padding: 10px;
}

.stPlotlyChart {
    background: white;
    border-radius: 18px;
    padding: 10px;
    box-shadow: 0 2px 10px rgba(0,0,0,0.04);
}

section[data-testid="stSidebar"] {
    background-color: #ffffff;
    border-right: 1px solid #ececec;
}

</style>
""", unsafe_allow_html=True)

# =========================
# TITLE
# =========================
st.title("📊 Quality Gate Preforming Monitoring System")

# =========================
# COLUMN FORMAT
# =========================
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

# =========================
# SESSION STATE
# =========================
if "db" not in st.session_state:
    st.session_state["db"] = pd.DataFrame(columns=COLUMNS)

# =========================
# SIDEBAR
# =========================
st.sidebar.header("📁 Data Management")

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

        st.sidebar.success("✅ Upload berhasil")

    except Exception as e:
        st.sidebar.error(f"Error : {e}")

# =========================
# INPUT FORM
# =========================
st.sidebar.header("➕ Input Data")

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

        st.success("✅ Data berhasil ditambahkan")

# =========================
# LOAD DATA
# =========================
df = st.session_state["db"].copy()

if df.empty:
    st.warning("Belum ada data")
    st.stop()

# =========================
# DATA CLEANING
# =========================
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

# =========================
# FILTER
# =========================
st.subheader("🔍 Filter Data")

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

# =========================
# KPI SCORECARD
# =========================
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

st.subheader("📌 Score Card")

k1,k2,k3,k4 = st.columns(4)

k1.metric(
    "Jumlah Layer Jalan",
    f"{jumlah_layer_jalan}"
)

k2.metric(
    "Jumlah Layer OK",
    f"{jumlah_layer_ok}"
)

k3.metric(
    "Jumlah Layer NG",
    f"{jumlah_layer_ng}"
)

k4.metric(
    "Akurasi OK",
    f"{akurasi_ok:.2%}"
)

# =========================
# COMBO CHART
# =========================
st.subheader("📈 Monitoring Harian")

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
        name="Jumlah Layer Jalan"
    ),

    secondary_y=False
)

fig_combo.add_trace(

    go.Scatter(
        x=daily["Tanggal"],
        y=daily["Akurasi"],
        mode="lines+markers",
        name="Akurasi OK"
    ),

    secondary_y=True
)

fig_combo.update_layout(
    height=450,
    template="plotly_white",
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

# =========================
# TOP TABLES
# =========================
t1,t2 = st.columns(2)

with t1:

    st.subheader("⚠️ 5 Mesin Hotpress Paling Bermasalah")

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

    top_hp.index = range(
        1,
        len(top_hp)+1
    )

    st.dataframe(
        top_hp,
        width="stretch",
        height=250
    )

with t2:

    st.subheader("⚠️ 5 Molding Paling Bermasalah")

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

    top_mold.index = range(
        1,
        len(top_mold)+1
    )

    st.dataframe(
        top_mold,
        width="stretch",
        height=250
    )

# =========================
# ANALYSIS CHART
# =========================
st.subheader("📊 Analisis Data")

g1,g2 = st.columns(2)

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
        height=420
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
        title="Distribusi Jenis Defect",
        hole=0.45
    )

    fig2.update_layout(
        template="plotly_white",
        height=420
    )

    st.plotly_chart(
        fig2,
        width="stretch"
    )

# =========================
# TABLE DATA
# =========================
st.subheader("📋 Tabel Data")

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

# =========================
# DELETE DATA
# =========================
st.subheader("🗑️ Hapus Data")

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

    st.success("✅ Data berhasil dihapus")

# =========================
# DOWNLOAD EXCEL
# =========================
st.subheader("⬇️ Download Data")

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
    label="📥 Download Excel",
    data=convert_excel(df),
    file_name="quality_gate.xlsx"
)
