import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime
import io

st.set_page_config(
    page_title="Quality Gate Monitoring",
    layout="wide"
)

st.markdown("""
<style>

    /* BACKGROUND */
    .stApp {
        background-color: #081F44;
        color: white;
    }

    /* TITLE */
    h1, h2, h3 {
        color: white !important;
        font-weight: 700;
    }

    /* SIDEBAR */
    section[data-testid="stSidebar"] {
        background-color: #710014;
    }

    section[data-testid="stSidebar"] * {
        color: white !important;
    }

    /* INPUT BOX */
    .stTextInput input,
    .stDateInput input,
    .stNumberInput input,
    .stSelectbox div[data-baseweb="select"] > div {
        background-color: #0B1733 !important;
        color: white !important;
        border: 1px solid #710014 !important;
        border-radius: 10px !important;
    }

    /* MULTISELECT */
    .stMultiSelect div[data-baseweb="select"] > div {
        background-color: #0B1733 !important;
        border-radius: 10px !important;
        border: 1px solid #710014 !important;
        color: white !important;
    }

    /* BUTTON */
    .stButton>button,
    .stDownloadButton>button,
    .stFormSubmitButton>button {
        background-color: #710014 !important;
        color: white !important;
        border-radius: 10px !important;
        border: none !important;
        font-weight: bold;
        transition: 0.3s;
    }

    .stButton>button:hover,
    .stDownloadButton>button:hover,
    .stFormSubmitButton>button:hover {
        background-color: #9b0020 !important;
        transform: scale(1.02);
    }

    /* METRIC CARD */
    div[data-testid="metric-container"] {
        background-color: #0B1733;
        border: 1px solid #710014;
        padding: 15px;
        border-radius: 15px;
    }

    /* DATAFRAME */
    .stDataFrame {
        border-radius: 15px;
        overflow: hidden;
    }

    /* LABEL */
    label {
        color: white !important;
        font-weight: 600;
    }

</style>
""", unsafe_allow_html=True)

st.title("Quality Gate Preforming Monitoring System")

COLUMNS = [
    "No","Tanggal","Shift","No HP","Layer HP",
    "Kode Mold","No Lot","Keterangan"
]

if "db" not in st.session_state:
    st.session_state["db"] = pd.DataFrame(columns=COLUMNS)

st.sidebar.header("Data Management")

uploaded_file = st.sidebar.file_uploader("Upload Excel", type=["xlsx"])

if uploaded_file:
    try:
        df_upload = pd.read_excel(uploaded_file)
        df_upload.columns = [str(c).strip() for c in df_upload.columns]
        df_upload = df_upload.loc[:, ~df_upload.columns.duplicated()]

        for col in COLUMNS:
            if col not in df_upload.columns:
                df_upload[col] = ""

        df_upload = df_upload[COLUMNS]
        df_upload["No"] = range(1, len(df_upload)+1)

        st.session_state["db"] = df_upload
        st.sidebar.success("Upload berhasil")

    except Exception as e:
        st.sidebar.error(f"Error : {e}")

st.sidebar.header("Input Data")

with st.sidebar.form("form", clear_on_submit=True):

    tgl = st.date_input(
        "Tanggal",
        datetime.today(),
        format="DD/MM/YYYY"
    )

    shift = st.selectbox("Shift", [1,2,3])
    hp = st.selectbox("No HP", [f"HP{i:02d}" for i in range(1,31)])
    layer = st.selectbox("Layer HP", [1,2,3,4,5])
    mold = st.text_input("Kode Mold")
    lot = st.text_input("No Lot")
    ket = st.selectbox("Keterangan", ["OK","Visual","Dimensi","Visual Dimensi"])

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
            [df.drop(columns=["No"], errors="ignore"), new],
            ignore_index=True
        )

        df["No"] = range(1, len(df)+1)

        st.session_state["db"] = df
        st.success("Data berhasil ditambahkan")

df = st.session_state["db"].copy()

if df.empty:
    st.warning("Belum ada data")
    st.stop()

df["Tanggal"] = pd.to_datetime(
    df["Tanggal"],
    format="%d/%m/%Y",
    errors="coerce"
)

df["is_ng"] = df["Keterangan"].astype(str).str.upper().ne("OK").astype(int)

st.subheader("Filter Data")

c1,c2,c3,c4 = st.columns(4)

with c1:
    f_shift = st.multiselect("Shift", sorted(df["Shift"].dropna().unique()))

with c2:
    f_hp = st.multiselect("No HP", sorted(df["No HP"].dropna().unique()))

with c3:
    f_ket = st.multiselect(
        "Keterangan",
        ["OK","Visual","Dimensi","Visual Dimensi"]
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
        (df_f["Tanggal"] >= pd.to_datetime(f_date[0])) &
        (df_f["Tanggal"] <= pd.to_datetime(f_date[1]))
    ]

total = len(df_f)
ng = int(df_f["is_ng"].sum())
ok = total - ng

defect = ng/total if total > 0 else 0
ok_rate = ok/total if total > 0 else 0

k1,k2,k3,k4 = st.columns(4)

k1.metric("Total Check", total)
k2.metric("Total NG", ng)
k3.metric("Persentase NG", f"{defect:.2%}")
k4.metric("Persentase OK", f"{ok_rate:.2%}")

st.subheader("5 Mesin Hotpress Paling Bermasalah")

top5 = (
    df_f.groupby("No HP")["is_ng"]
    .sum()
    .reset_index()
    .rename(columns={
        "No HP":"Mesin Hotpress",
        "is_ng":"Jumlah NG"
    })
    .sort_values(by="Jumlah NG", ascending=False)
    .head(5)
)

top5.index = range(1, len(top5)+1)

st.dataframe(
    top5,
    width="stretch",
    height=250
)

st.subheader("Analisis Data")

g1,g2 = st.columns(2)

with g1:
    mesin = df_f.groupby("No HP")["is_ng"].sum().reset_index()

    fig1 = px.bar(
        mesin,
        x="No HP",
        y="is_ng",
        title="NG per Mesin",
        text_auto=True,
        color_discrete_sequence=["#710014"]
    )

    fig1.update_layout(
        plot_bgcolor="#0B1733",
        paper_bgcolor="#0B1733",
        font_color="white"
    )

    st.plotly_chart(fig1, width="stretch", theme=None)

with g2:
    cacat = df_f[df_f["is_ng"] == 1]["Keterangan"].value_counts().reset_index()
    cacat.columns = ["Jenis Cacat", "Jumlah"]

    fig2 = px.pie(
        cacat,
        names="Jenis Cacat",
        values="Jumlah",
        title="Distribusi Defect",
        hole=0.45,
        color_discrete_sequence=[
            "#710014",
            "#9b0020",
            "#C1121F",
            "#081F44"
        ]
    )

    fig2.update_layout(
        plot_bgcolor="#0B1733",
        paper_bgcolor="#0B1733",
        font_color="white"
    )

    st.plotly_chart(fig2, width="stretch", theme=None)

st.subheader("Tabel Data")

# FORMAT TAMPIL TANGGAL
df_show = df_f.copy()
df_show["Tanggal"] = df_show["Tanggal"].dt.strftime("%d/%m/%Y")

st.dataframe(
    df_show[COLUMNS],
    width="stretch",
    height=450
)

st.subheader("Hapus Data")

hapus = st.number_input(
    "Masukkan Nomor Data",
    min_value=1,
    step=1
)

if st.button("Hapus"):
    df = st.session_state["db"]
    df = df[df["No"] != hapus]
    df["No"] = range(1, len(df)+1)

    st.session_state["db"] = df
    st.success("Data berhasil dihapus")

st.subheader("Download Data")

def convert_excel(data):

    export = data.copy()

    export["Tanggal"] = pd.to_datetime(
        export["Tanggal"],
        errors="coerce"
    ).dt.strftime("%d/%m/%Y")

    output = io.BytesIO()

    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        export[COLUMNS].to_excel(writer, index=False)

    return output.getvalue()

st.download_button(
    label="Download Excel",
    data=convert_excel(df),
    file_name="quality_gate.xlsx"
)
