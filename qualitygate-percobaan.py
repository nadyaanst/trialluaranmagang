# =========================
# CUSTOM CSS PROFESSIONAL DASHBOARD
# =========================
st.markdown("""
<style>

/* ===== GOOGLE FONT ===== */
@import url('https://fonts.googleapis.com/css2?family=Barlow:wght@400;500;600;700;800&display=swap');

html, body, [class*="css"] {
    font-family: 'Barlow', sans-serif;
}

/* ===== MAIN BACKGROUND ===== */
.main {
    background-color: #f1f3f8;
}

/* ===== CONTAINER ===== */
.block-container {
    padding-top: 1rem;
    padding-bottom: 1rem;
    max-width: 100%;
}

/* ===== HEADER ===== */
.dashboard-header {
    background: white;
    padding: 18px 30px;
    border-radius: 14px;
    border-left: 8px solid #c1121f;
    box-shadow: 0 2px 12px rgba(0,0,0,0.08);
    margin-bottom: 20px;
}

.dashboard-title {
    font-size: 40px;
    font-weight: 800;
    color: #111111;
    letter-spacing: 1px;
    margin-bottom: 2px;
}

.dashboard-subtitle {
    font-size: 16px;
    color: #6b7280;
    font-weight: 500;
}

/* ===== SIDEBAR ===== */
section[data-testid="stSidebar"] {
    background: linear-gradient(
        180deg,
        #1d2f6f 0%,
        #243b8a 100%
    );
    border-right: none;
}

section[data-testid="stSidebar"] * {
    color: white !important;
    font-family: 'Barlow', sans-serif;
}

section[data-testid="stSidebar"] label {
    font-weight: 600 !important;
}

/* ===== CARD ===== */
.card {
    background: white;
    border-radius: 18px;
    padding: 18px;
    box-shadow: 0 4px 18px rgba(0,0,0,0.08);
    border-top: 6px solid #1d2f6f;
    margin-bottom: 18px;
}

.card-red {
    border-top: 6px solid #c1121f;
}

.card-title {
    font-size: 18px;
    font-weight: 700;
    color: #1d2f6f;
    margin-bottom: 14px;
    text-transform: uppercase;
    letter-spacing: 0.5px;
}

/* ===== KPI CARD ===== */
.kpi-card {
    background: white;
    border-radius: 18px;
    padding: 22px;
    text-align: center;
    box-shadow: 0 4px 18px rgba(0,0,0,0.08);
    border-top: 8px solid #1d2f6f;
}

.kpi-red {
    border-top: 8px solid #c1121f;
}

.kpi-title {
    font-size: 15px;
    font-weight: 700;
    color: #6b7280;
    text-transform: uppercase;
    margin-bottom: 8px;
    letter-spacing: 0.5px;
}

.kpi-value {
    font-size: 38px;
    font-weight: 800;
    color: #111111;
}

/* ===== TABLE ===== */
[data-testid="stDataFrame"] {
    border-radius: 16px;
    overflow: hidden;
    border: 1px solid #dbe2ef;
}

/* ===== CHART ===== */
.stPlotlyChart {
    background: white;
    border-radius: 18px;
    padding: 10px;
    box-shadow: 0 4px 18px rgba(0,0,0,0.08);
}

/* ===== SECTION TITLE ===== */
.section-title {
    font-size: 24px;
    font-weight: 800;
    color: #1d2f6f;
    margin-top: 10px;
    margin-bottom: 16px;
    text-transform: uppercase;
}

/* ===== BUTTON ===== */
.stButton > button {
    width: 100%;
    background-color: #c1121f;
    color: white;
    border-radius: 10px;
    border: none;
    height: 45px;
    font-weight: 700;
    transition: 0.3s;
}

.stButton > button:hover {
    background-color: #9b0d18;
    color: white;
}

/* ===== DOWNLOAD BUTTON ===== */
.stDownloadButton > button {
    width: 100%;
    background-color: #1d2f6f;
    color: white;
    border-radius: 10px;
    border: none;
    height: 45px;
    font-weight: 700;
}

.stDownloadButton > button:hover {
    background-color: #162452;
    color: white;
}

</style>
""", unsafe_allow_html=True)

# =========================
# HEADER
# =========================
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

# =========================
# FILTER TITLE
# =========================
st.markdown("""
<div class="section-title">
    FILTER DATA
</div>
""", unsafe_allow_html=True)

# =========================
# SCORE CARD TITLE
# =========================
st.markdown("""
<div class="section-title">
    PERFORMANCE OVERVIEW
</div>
""", unsafe_allow_html=True)

# =========================
# KPI CUSTOM DESIGN
# =========================
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
    <div class="kpi-card kpi-red">
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

# =========================
# COMBO CHART TITLE
# =========================
st.markdown("""
<div class="section-title">
    TREND HARIAN LAYER DAN AKURASI
</div>
""", unsafe_allow_html=True)

# =========================
# COMBO CHART STYLE
# =========================
fig_combo.update_layout(

    paper_bgcolor="white",
    plot_bgcolor="white",

    font=dict(
        family="Barlow",
        size=13,
        color="#111111"
    ),

    title_font=dict(
        size=22,
        family="Barlow",
        color="#1d2f6f"
    ),

    legend=dict(
        orientation="h",
        yanchor="bottom",
        y=1.02,
        xanchor="left",
        x=0
    ),

    margin=dict(
        l=30,
        r=30,
        t=30,
        b=20
    ),

    height=500
)

fig_combo.update_traces(
    marker_color="#1d2f6f"
)

fig_combo.data[1].line.color = "#c1121f"
fig_combo.data[1].line.width = 4

fig_combo.update_xaxes(
    showgrid=False,
    linecolor="#cfcfcf"
)

fig_combo.update_yaxes(
    gridcolor="#e5e7eb"
)

st.plotly_chart(
    fig_combo,
    width="stretch"
)

# =========================
# TOP TABLE SECTION
# =========================
st.markdown("""
<div class="section-title">
    TOP PROBLEM ANALYSIS
</div>
""", unsafe_allow_html=True)

t1,t2 = st.columns(2)

with t1:

    st.markdown("""
    <div class="card">
        <div class="card-title">
            Top 5 Mesin Hotpress Paling Bermasalah
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.dataframe(
        top_hp,
        width="stretch",
        height=260
    )

with t2:

    st.markdown("""
    <div class="card card-red">
        <div class="card-title">
            Top 5 Molding Paling Bermasalah
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.dataframe(
        top_mold,
        width="stretch",
        height=260
    )

# =========================
# ANALYSIS TITLE
# =========================
st.markdown("""
<div class="section-title">
    DEFECT DISTRIBUTION ANALYSIS
</div>
""", unsafe_allow_html=True)

# =========================
# CHART STYLE
# =========================
fig1.update_layout(
    paper_bgcolor="white",
    plot_bgcolor="white",

    font=dict(
        family="Barlow",
        size=13,
        color="#111111"
    ),

    title_font=dict(
        size=20,
        color="#1d2f6f"
    ),

    margin=dict(
        l=20,
        r=20,
        t=60,
        b=20
    ),

    height=450
)

fig1.update_traces(
    marker_color="#1d2f6f"
)

fig2.update_layout(
    paper_bgcolor="white",

    font=dict(
        family="Barlow",
        size=13,
        color="#111111"
    ),

    title_font=dict(
        size=20,
        color="#c1121f"
    ),

    height=450
)

# =========================
# TABLE TITLE
# =========================
st.markdown("""
<div class="section-title">
    DETAIL DATA MONITORING
</div>
""", unsafe_allow_html=True)

# =========================
# DELETE TITLE
# =========================
st.markdown("""
<div class="section-title">
    DELETE DATA
</div>
""", unsafe_allow_html=True)

# =========================
# DOWNLOAD TITLE
# =========================
st.markdown("""
<div class="section-title">
    EXPORT DATA
</div>
""", unsafe_allow_html=True)
