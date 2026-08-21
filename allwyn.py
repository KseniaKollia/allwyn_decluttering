import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import urllib.parse

# ---------------------------------------------------------
# 1. ΡΥΘΜΙΣΗ ΣΕΛΙΔΑΣ & DESIGN
# ---------------------------------------------------------
st.set_page_config(
    page_title="DECLUTTERING QUESTION",
    layout="wide",
    page_icon="📈"
)

st.markdown("""
    <style>
    /* Εισαγωγή της γραμματοσειράς Outfit από το Google Fonts */
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@800;900&display=swap');

    /* Background της εφαρμογής */
    .stApp { 
        background-color: #112229; 
        color: #FFFFFF; 
    }

    /* ΠΕΡΙΓΡΑΜΜΑ ΣΕ ΟΛΟ ΤΟ DASHBOARD (#2FDDC0) */
    .main .block-container {
        border: 2px solid #2FDDC0 !important;
        border-radius: 15px !important;
        padding: 30px !important;
        margin-top: 15px !important;
        background-color: #112229 !important;
        box-shadow: 0 0 15px rgba(47, 221, 192, 0.2) !important;
    }

    /* HEADER BANNER (#1A333D) */
    div[data-testid="stHorizontalBlock"]:has(.header-text-style) {
        background-color: #1A333D !important;
        padding: 15px 20px !important;
        align-items: center !important;
        border-radius: 10px !important;
        border: 1px solid #2FDDC0 !important;
    }

    /* ΤΙΤΛΟΣ ΜΕ ΓΡΑΜΜΑΤΟΣΕΙΡΑ ΤΥΠΟΥ ALLWYN */
    .header-text-style {
        color: #FFFFFF !important;
        font-family: 'Outfit', sans-serif !important;
        font-weight: 900 !important;
        font-size: 38px !important;
        text-transform: uppercase !important; /* Κάνει τους χαρακτήρες κεφαλαίους όπως το brand */
        text-align: center !important;
        letter-spacing: 1px !important;
        margin: 0 !important;
        padding: 0 !important;
        display: block !important;
        width: 100% !important;
    }

    /* SIDEBAR STYLING (#09A1A4) */
    [data-testid="stSidebar"] {
        background-color: #0E1A1F !important;
    }

    [data-testid="stSidebar"] *, 
    [data-testid="stSidebar"] label, 
    [data-testid="stSidebar"] label p,
    [data-testid="stSidebar"] h1, 
    [data-testid="stSidebar"] h2, 
    [data-testid="stSidebar"] h3 {
        color: #09A1A4 !important;
        font-weight: bold !important;
    }

    [data-testid="stSidebar"] div[data-baseweb="select"] > div { 
        background-color: #1A333D !important; 
        border: 1px solid #09A1A4 !important;
    }
    
    [data-testid="stSidebar"] div[data-baseweb="select"] span {
        color: #FFFFFF !important;
    }

    /* METRICS STYLING (#1A333D) */
    [data-testid="stMetric"] { 
        background-color: #1A333D !important; 
        padding: 15px !important; 
        border-radius: 8px !important; 
        border: 2px solid #2FDDC0 !important;
    }
    [data-testid="stMetricLabel"] p { color: #2FDDC0 !important; font-weight: bold; }
    [data-testid="stMetricValue"] div { color: #FFFFFF !important; }

    .stApp h1, .stApp h2, .stApp h3, .stApp h4, .stApp h5, .stApp h6, 
    .stApp label, .stApp p, .stApp span { 
        color: #FFFFFF; 
    }
    </style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# 2. ΑΣΦΑΛΕΙΑ ΜΕ ΚΩΔΙΚΟ
# ---------------------------------------------------------
def check_password():
    if "password_correct" not in st.session_state:
        st.session_state["password_correct"] = False

    if st.session_state["password_correct"]:
        return True

    st.title("🔒 Περιοχή Πρόσβασης Πελάτη")
    st.write("Please insert the password.")
    
    with st.form("login_form"):
        password_input = st.text_input("Password:", type="password")
        submit_button = st.form_submit_button("Connect")
        
        if submit_button:
            expected_password = st.secrets.get("CLIENT_PASSWORD", "AllwynDQ@")
            if password_input == expected_password:
                st.session_state["password_correct"] = True
                st.rerun()
            else:
                st.error("🚨 Wrong password.")
            
    return False

if not check_password():
    st.stop()

# ---------------------------------------------------------
# 3. ΦΟΡΤΩΣΗ ΔΕΔΟΜΕΝΩΝ
# ---------------------------------------------------------
SHEET_ID = "1Aw83hnkXT8yaXkKbpVAiCTx7AXT0Z-GXgAwS6r1itNs"

@st.cache_data(ttl=60)
def load_sheet_data(worksheet_name):
    encoded_sheet_name = urllib.parse.quote(worksheet_name)
    url = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet={encoded_sheet_name}"
    df = pd.read_csv(url)
    df.columns = [str(c).strip() for c in df.columns]
    return df

try:
    df_opap = load_sheet_data("OPAP ΕΡΩΤΗΣΗ 2000")
    df_stores = load_sheet_data("STORE STATUS (WEEKLY)")
except Exception as e:
    st.error(f"Error loading Google Sheet: {e}")
    st.stop()

if "DATE" in df_opap.columns:
    df_opap["DATE_DT"] = pd.to_datetime(df_opap["DATE"], format="%d/%m/%Y", errors='coerce')
    df_opap["DATE_DT"] = df_opap["DATE_DT"].fillna(pd.to_datetime(df_opap["DATE"], dayfirst=True, errors='coerce'))
    df_opap["MONTH"] = df_opap["DATE_DT"].dt.strftime('%B %Y')

if "WEEK" in df_opap.columns:
    df_opap["WEEK_NUM"] = pd.to_numeric(df_opap["WEEK"].astype(str).str.extract(r'(\d+)')[0], errors='coerce')

# ---------------------------------------------------------
# 4. LOGOS & HEADER BANNER
# ---------------------------------------------------------
header_col1, header_col2, header_col3 = st.columns([1, 4, 1], vertical_alignment="center")

with header_col1:
    try:
        st.image("WEST_logo.png", use_container_width=True)
    except Exception:
        pass

with header_col2:
    st.markdown('<div class="header-text-style">Allwyn Decluttering Dashboard</div>', unsafe_allow_html=True)

with header_col3:
    try:
        st.image("ALLWYN_logo.png", use_container_width=True)
    except Exception:
        pass

st.markdown("---")

# ---------------------------------------------------------
# 5. SIDEBAR - ΦΙΛΤΡΑ (#09A1A4 STYLING) & EXPORT DATA
# ---------------------------------------------------------
st.sidebar.header("⚙️ Dashboard Filters")

months_order = [m for m in df_opap["MONTH"].unique() if pd.notna(m)] if "MONTH" in df_opap.columns else []
selected_months = st.sidebar.multiselect("MONTH (Μήνας)", options=months_order, default=[])

if selected_months:
    df_month_filtered = df_opap[df_opap["MONTH"].isin(selected_months)]
else:
    df_month_filtered = df_opap.copy()

if "WEEK_NUM" in df_month_filtered.columns:
    available_weeks = sorted([int(x) for x in df_month_filtered["WEEK_NUM"].dropna().unique()])
else:
    available_weeks = []

selected_weeks = st.sidebar.multiselect("WEEK (Εβδομάδα)", options=available_weeks, default=[])

if selected_weeks:
    df_filtered = df_month_filtered[df_month_filtered["WEEK_NUM"].isin(selected_weeks)]
else:
    df_filtered = df_month_filtered.copy()

# EXPORT DATA (SIDEBAR)
st.sidebar.markdown("---")
st.sidebar.header("📥 Export Data")

@st.cache_data
def convert_df_to_csv(df):
    return df.to_csv(index=False).encode('utf-8-sig')

csv_data = convert_df_to_csv(df_filtered)

st.sidebar.download_button(
    label="Download Data (CSV)",
    data=csv_data,
    file_name="decluttering_data_export.csv",
    mime="text/csv"
)

# ---------------------------------------------------------
# 6. ΔΙΑΓΡΑΜΜΑ 1: NETWORK COVERAGE
# ---------------------------------------------------------
st.subheader("NETWORK COVERAGE")

if not df_opap.empty:
    df_opap_clean = df_opap.dropna(subset=["ID"]).copy()
    df_opap_clean["ID"] = df_opap_clean["ID"].astype(str).str.strip()

    df_filtered_period = df_opap_clean.copy()
    
    if selected_months:
        df_filtered_period = df_filtered_period[df_filtered_period["MONTH"].isin(selected_months)]
    
    if selected_weeks:
        df_filtered_period = df_filtered_period[df_filtered_period["WEEK_NUM"].isin(selected_weeks)]

    sort_cols = [c for c in ["WEEK_NUM", "DATE_DT"] if c in df_filtered_period.columns]
    if sort_cols:
        df_sorted = df_filtered_period.sort_values(by=sort_cols, ascending=True)
    else:
        df_sorted = df_filtered_period.copy()

    df_last_responses = df_sorted.drop_duplicates(subset=["ID"], keep="last")

    if "ACTIVITY" in df_stores.columns and "ID" in df_stores.columns:
        df_stores_clean = df_stores.dropna(subset=["ID"]).copy()
        df_stores_clean["ID"] = df_stores_clean["ID"].astype(str).str.strip()
        df_last_status = df_stores_clean.drop_duplicates(subset=["ID"], keep="last")
        
        df_merged = pd.merge(
            df_last_responses,
            df_last_status[["ID", "ACTIVITY"]],
            on="ID",
            how="left"
        )
    else:
        df_merged = df_last_responses.copy()
        df_merged["ACTIVITY"] = "ACTIVE"

    df_active = df_merged[df_merged["ACTIVITY"].astype(str).str.strip().str.upper() == "ACTIVE"]
    total_active_ids = len(df_active)

    valid_answers = ["ΝΑΙ", "ΔΕΝ ΥΠΗΡΧΕ ΠΑΛΑΙΟ-ΜΗ ΕΓΚΕΚΡΙΜΕΝΟ ΥΛΙΚΟ"]
    decluttered_ids = df_active[df_active["ANSWER"].isin(valid_answers)]["ID"].unique()
    
    decluttered_count = len(decluttered_ids)
    remaining_active = max(0, total_active_ids - decluttered_count)
    coverage_pct = (decluttered_count / total_active_ids * 100) if total_active_ids > 0 else 0

    c1, c2, c3 = st.columns(3)
    c1.metric("Total active IDs", f"{total_active_ids:,}")
    c2.metric("Decluttered", f"{decluttered_count:,}")
    c3.metric("Coverage %", f"{coverage_pct:.1f}%")

    fig_coverage = go.Figure()

    fig_coverage.add_trace(go.Bar(
        y=["Network Coverage"],
        x=[decluttered_count],
        name="Decluttered",
        orientation='h',
        marker=dict(color='#2FDDC0'),
        text=f"{decluttered_count:,}",
        textposition='inside',
        insidetextfont=dict(color='white', size=13),
        cliponaxis=False
    ))

    fig_coverage.add_trace(go.Bar(
        y=["Network Coverage"],
        x=[remaining_active],
        name="Remaining",
        orientation='h',
        marker=dict(color='#115566'),
        text=f"{remaining_active:,}" if remaining_active > 0 else "",
        textposition='inside',
        insidetextfont=dict(color='white', size=13),
        cliponaxis=False
    ))

    fig_coverage.update_layout(
        barmode='stack',
        height=180,
        margin=dict(l=20, r=20, t=30, b=20),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(color='white'),
        xaxis=dict(
            range=[0, max(total_active_ids, decluttered_count) * 1.02 if total_active_ids > 0 else 100],
            title="Total Active IDs",
            showgrid=False,
            color='white'
        ),
        yaxis=dict(color='white'),
        showlegend=True,
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1, font=dict(color='white'))
    )

    st.plotly_chart(fig_coverage, use_container_width=True)

# ---------------------------------------------------------
# 7. ΑΝΑΖΗΤΗΣΗ STORE ID
# ---------------------------------------------------------
st.subheader("🔍 Search Store ID")

if "ID" in df_opap.columns:
    id_counts = df_opap.groupby("ID").size().to_dict()
    
    formatted_options = []
    store_map = {}
    
    sorted_ids = sorted([str(x) for x in df_opap["ID"].dropna().unique()])
    
    for sid in sorted_ids:
        count = id_counts.get(int(sid) if sid.isdigit() else sid, 0)
        label = f"{sid} — ({count} weeks)"
        formatted_options.append(label)
        store_map[label] = sid

    selected_option = st.selectbox(
        "Select or Search Store ID:",
        options=["-- Choose Store ID --"] + formatted_options
    )

    if selected_option != "-- Choose Store ID --":
        selected_store_id = store_map[selected_option]
        df_single_store = df_opap[df_opap["ID"].astype(str) == selected_store_id].copy()
        
        if "WEEK_NUM" in df_single_store.columns:
            df_single_store = df_single_store.sort_values(by="WEEK_NUM")
            
        total_visits = len(df_single_store)
        unique_weeks_count = df_single_store["WEEK_NUM"].nunique() if "WEEK_NUM" in df_single_store.columns else 0

        s_col1, s_col2 = st.columns(2)
        s_col1.metric("Total Visits", total_visits)
        s_col2.metric("Visited in Weeks (Count)", f"{unique_weeks_count} weeks")

        st.write(f"**History for Store ID:** `{selected_store_id}`")
        display_cols = [c for c in ["WEEK", "DATE", "MONTH", "STATUS", "ANSWER"] if c in df_single_store.columns]
        st.dataframe(df_single_store[display_cols], use_container_width=True, hide_index=True)

# ---------------------------------------------------------
# 8. ΔΙΑΓΡΑΜΜΑ 2: WEEKLY STACKED BAR
# ---------------------------------------------------------
st.subheader("ΑΦΑΙΡΕΘΗΚΕ ΤΥΧΟΝ ΤΟΠΟΘΕΤΗΜΕΝΟ ΠΑΛΑΙΟ Η ΜΗ ΕΓΚΡΚΡΙΜΕΝΟ ΥΛΙΚΟ (ΑΦΙΣΕΣ) ΑΠΟ ΤΟ ΚΑΤΑΣΤΗΜΑ ?")

if "WEEK_NUM" in df_filtered.columns and "ANSWER" in df_filtered.columns and not df_filtered.empty:
    df_chart = df_filtered.groupby(["WEEK_NUM", "ANSWER"]).size().reset_index(name="Count")
    df_chart = df_chart.sort_values(by="WEEK_NUM")
    df_chart["WEEK_LABEL"] = "Week " + df_chart["WEEK_NUM"].astype(int).astype(str)

    totals = df_chart.groupby("WEEK_LABEL")["Count"].sum().reset_index(name="Total")

    color_map = {
        "ΝΑΙ": "#2FDDC0",
        "ΔΕΝ ΥΠΗΡΧΕ ΠΑΛΑΙΟ-ΜΗ ΕΓΚΕΚΡΙΜΕΝΟ ΥΛΙΚΟ": "#09A1A4",
        "ΟΧΙ": "#115566"
    }

    fig_weekly = px.bar(
        df_chart,
        x="WEEK_LABEL",
        y="Count",
        color="ANSWER",
        color_discrete_map=color_map
    )

    fig_weekly.update_traces(
        hovertemplate="<b>%{x}</b><br>%{fullData.name}: <b>%{y:,}</b><extra></extra>"
    )

    for _, row in totals.iterrows():
        fig_weekly.add_annotation(
            x=row["WEEK_LABEL"],
            y=row["Total"],
            text=f"{row['Total']:,}",
            showarrow=False,
            yshift=10,
            font=dict(color="white", size=13, family="Arial Black")
        )

    max_y = totals["Total"].max() * 1.15 if not totals.empty else 100

    fig_weekly.update_layout(
        barmode='stack',
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(color='white'),
        xaxis_title="Week",
        yaxis_title="Total Answers",
        legend_title_text="",
        legend=dict(orientation="h", yanchor="bottom", y=1.05, xanchor="right", x=1, font=dict(color='white')),
        height=540,
        xaxis=dict(
            showgrid=False,
            type='category',
            color='white'
        ),
        yaxis=dict(
            showgrid=False,
            color='white',
            range=[0, max_y]
        )
    )

    st.plotly_chart(fig_weekly, use_container_width=True)
else:
    st.info("No data available for the selected filters.")


# ---------------------------------------------------------
# 9. ΧΑΡΤΗΣ ΚΑΛΥΨΗΣ ΑΝΑ REGION (BASED ON UNIQUE STORES LIKE NETWORK COVERAGE)
# ---------------------------------------------------------
if "REGION" in df_opap.columns and not df_opap.empty:
    st.markdown("---")
    st.subheader("🗺️ COVERAGE MAP BY REGION")

    REGION_COORDINATES = {
        "ΑΤΤΙΚΗΣ - ΑΤΤΙΚΗΣ": (37.9838, 23.7275),
        "ΚΕΝΤΡΙΚΗΣ ΜΑΚΕΔΟΝΙΑΣ - ΣΕΡΡΩΝ": (41.0849, 23.5476),
        "ΚΕΝΤΡΙΚΗΣ ΜΑΚΕΔΟΝΙΑΣ - ΘΕΣΣΑΛΟΝΙΚΗΣ": (40.6401, 22.9444),
        "ΗΠΕΙΡΟΥ - ΙΩΑΝΝΙΝΩΝ": (39.6650, 20.8537),
        "ΘΕΣΣΑΛΙΑΣ - ΛΑΡΙΣΗΣ": (39.6390, 22.4191),
        "ΘΕΣΣΑΛΙΑΣ - ΜΑΓΝΗΣΙΑΣ": (39.3621, 22.9422),
        "ΠΕΛΟΠΟΝΝΗΣΟΥ - ΑΡΓΟΛΙΔΟΣ": (37.5672, 22.8014),
        "ΚΡΗΤΗΣ - ΗΡΑΚΛΕΙΟΥ": (35.3387, 25.1442),
        "ΗΠΕΙΡΟΥ - ΑΡΤΗΣ": (39.1606, 20.9853),
        "ΣΤΕΡΕΑΣ ΕΛΛΑΔΑΣ - ΦΘΙΩΤΙΔΟΣ": (38.8986, 22.4331),
        "ΑΝΑΤΟΛΙΚΗΣ ΜΑΚΕΔΟΝΙΑΣ ΚΑΙ ΘΡΑΚΗΣ - ΚΑΒΑΛΑΣ": (40.9396, 24.4069),
        "ΗΠΕΙΡΟΥ - ΘΕΣΠΡΩΤΙΑΣ": (39.5039, 20.2656),
        "ΠΕΛΟΠΟΝΝΗΣΟΥ - ΚΟΡΙΝΘΙΑΣ": (37.9386, 22.9322),
        "ΑΝΑΤΟΛΙΚΗΣ ΜΑΚΕΔΟΝΙΑΣ ΚΑΙ ΘΡΑΚΗΣ - ΞΑΝΘΗΣ": (41.1349, 24.8880),
        "ΘΕΣΣΑΛΙΑΣ - ΤΡΙΚΑΛΩΝ": (39.5549, 21.7684),
        "ΠΕΛΟΠΟΝΝΗΣΟΥ - ΑΡΚΑΔΙΑΣ": (37.5103, 22.3726),
        "ΙΟΝΙΩΝ ΝΗΣΩΝ - ΚΕΡΚΥΡΑΣ": (39.6243, 19.9217),
        "ΑΝΑΤΟΛΙΚΗΣ ΜΑΚΕΔΟΝΙΑΣ ΚΑΙ ΘΡΑΚΗΣ - ΔΡΑΜΑΣ": (41.1511, 24.1403),
        "ΔΥΤΙΚΗΣ ΜΑΚΕΔΟΝΙΑΣ - ΚΟΖΑΝΗΣ": (40.3006, 21.7889),
        "ΠΕΛΟΠΟΝΝΗΣΟΥ - ΜΕΣΣΗΝΙΑΣ": (37.0389, 22.1142),
        "ΘΕΣΣΑΛΙΑΣ - ΚΑΡΔΙΤΣΗΣ": (39.3644, 21.9214),
        "ΔΥΤΙΚΗΣ ΕΛΛΑΔΑΣ - ΑΧΑΪΑΣ": (38.2466, 21.7345),
        "ΑΝΑΤΟΛΙΚΗΣ ΜΑΚΕΔΟΝΙΑΣ ΚΑΙ ΘΡΑΚΗΣ - ΕΒΡΟΥ": (40.8457, 25.8739),
        "ΣΤΕΡΕΑΣ ΕΛΛΑΔΑΣ - ΒΟΙΩΤΙΑΣ": (38.4378, 22.8756),
        "ΠΕΛΟΠΟΝΝΗΣΟΥ - ΛΑΚΩΝΙΑΣ": (37.0733, 22.4297),
        "ΗΠΕΙΡΟΥ - ΠΡΕΒΕΖΗΣ": (38.9569, 20.7506),
        "ΣΤΕΡΕΑΣ ΕΛΛΑΔΑΣ - ΕΥΒΟΙΑΣ": (38.4636, 23.5991),
        "ΚΕΝΤΡΙΚΗΣ ΜΑΚΕΔΟΝΙΑΣ - ΗΜΑΘΙΑΣ": (40.5244, 22.2022),
        "ΔΥΤΙΚΗΣ ΜΑΚΕΔΟΝΙΑΣ - ΦΛΩΡΙΝΗΣ": (40.7819, 21.4098),
        "ΚΡΗΤΗΣ - ΧΑΝΙΩΝ": (35.5138, 24.0180),
        "ΑΝΑΤΟΛΙΚΗΣ ΜΑΚΕΔΟΝΙΑΣ ΚΑΙ ΘΡΑΚΗΣ - ΡΟΔΟΠΗΣ": (41.1186, 25.4042),
        "ΚΕΝΤΡΙΚΗΣ ΜΑΚΕΔΟΝΙΑΣ - ΚΙΛΚΙΣ": (40.9930, 22.8753),
        "ΚΕΝΤΡΙΚΗΣ ΜΑΚΕΔΟΝΙΑΣ - ΠΕΛΛΗΣ": (40.8017, 22.0439),
        "ΒOΡΕΙΟΥ ΑΙΓΑΙΟΥ - ΛΕΣΒΟΥ": (39.1042, 26.5550),
        "ΚΕΝΤΡΙΚΗΣ ΜΑΚΕΔΟΝΙΑΣ - ΠΙΕΡΙΑΣ": (40.2696, 22.5061),
        "ΚΕΝΤΡΙΚΗΣ ΜΑΚΕΔΟΝΙΑΣ - ΧΑΛΚΙΔΙΚΗΣ": (40.3783, 23.4428),
        "ΚΡΗΤΗΣ - ΡΕΘΥΜΝΗΣ": (35.3672, 24.4739),
        "ΔΥΤΙΚΗΣ ΕΛΛΑΔΑΣ - ΗΛΕΙΑΣ": (37.6726, 21.4402),
        "ΔΥΤΙΚΗΣ ΕΛΛΑΔΑΣ - ΑΙΤΩΛΙΑΣ ΚΑΙ ΑΚΑΡΝΑΝΙΑΣ": (38.6247, 21.4089),
        "ΙΟΝΙΩΝ ΝΗΣΩΝ - ΛΕΥΚΑΔΟΣ": (38.8304, 20.7044),
        "ΒOΡΕΙΟΥ ΑΙΓΑΙΟΥ - ΧΙΟΥ": (38.3678, 26.1358),
        "ΝOΤΙΟΥ ΑΙΓΑΙΟΥ - ΚΥΚΛΑΔΩΝ": (37.4437, 24.9422),
        "ΔΥΤΙΚΗΣ ΜΑΚΕΔΟΝΙΑΣ - ΓΡΕΒΕΝΩΝ": (40.0839, 21.4275),
        "ΔΥΤΙΚΗΣ ΜΑΚΕΔΟΝΙΑΣ - ΚΑΣΤΟΡΙΑΣ": (40.5216, 21.2634),
        "ΣΤΕΡΕΑΣ ΕΛΛΑΔΑΣ - ΦΩΚΙΔΟΣ": (38.5286, 22.3769),
        "ΝOΤΙΟΥ ΑΙΓΑΙΟΥ - ΔΩΔΕΚΑΝΗΣΟΥ": (36.4349, 28.2175),
        "ΙOΝΙΩΝ ΝΗΣΩΝ - ΚΕΦΑΛΛΗΝΙΑΣ": (38.1772, 20.4883),
        "ΒOΡΕΙΟΥ ΑΙΓΑΙΟΥ - ΣΑΜΟΥ": (37.7548, 26.9778),
        "ΚΡΗΤΗΣ - ΛΑΣΙΘΙΟΥ": (35.1653, 25.7153),
        "ΙOΝΙΩΝ ΝΗΣΩΝ - ΖΑΚΥΝΘΟΥ": (37.7870, 20.8979),
        "ΣΤΕΡΕΑΣ ΕΛΛΑΔΑΣ - ΕΥΡΥΤΑΝΙΑΣ": (38.9122, 21.7981)
    }

    # Χρήση του df_active που έχει ήδη υπολογιστεί σωστά στο Section 6
    # Φιλτράρισμα μόνο των έγκυρων απαντήσεων decluttering
    valid_answers = ["ΝΑΙ", "ΔΕΝ ΥΠΗΡΧΕ ΠΑΛΑΙΟ-ΜΗ ΕΓΚΕΚΡΙΜΕΝΟ ΥΛΙΚΟ"]
    
    # 1. Υπολογισμός συνολικών ACTIVE καταστημάτων ανά REGION
    df_map_total = df_active.groupby("REGION")["ID"].nunique().reset_index(name="Total_Stores")

    # 2. Υπολογισμός DECLUTTERED καταστημάτων ανά REGION
    df_decluttered_stores = df_active[df_active["ANSWER"].isin(valid_answers)]
    df_map_decluttered = df_decluttered_stores.groupby("REGION")["ID"].nunique().reset_index(name="Decluttered_Stores")

    # 3. Merge για το τελικό dataframe του χάρτη
    df_map = pd.merge(df_map_total, df_map_decluttered, on="REGION", how="left")
    df_map["Decluttered_Stores"] = df_map["Decluttered_Stores"].fillna(0).astype(int)

    # 4. Υπολογισμός ποσοστού Coverage %
    df_map["Coverage %"] = (df_map["Decluttered_Stores"] / df_map["Total_Stores"] * 100).round(1)

    # 5. Αντιστοίχιση συντεταγμένων
    df_map["lat"] = df_map["REGION"].map(lambda x: REGION_COORDINATES.get(str(x).strip(), (None, None))[0])
    df_map["lon"] = df_map["REGION"].map(lambda x: REGION_COORDINATES.get(str(x).strip(), (None, None))[1])

    df_map_clean = df_map.dropna(subset=["lat", "lon"]).copy()

    if not df_map_clean.empty:
        fig_map = px.scatter_mapbox(
            df_map_clean,
            lat="lat",
            lon="lon",
            size="Total_Stores",
            color="Coverage %",
            color_continuous_scale=["#115566", "#09A1A4", "#2FDDC0"],
            range_color=[0, 100],  # Σταθερό scale 0-100%
            size_max=38,
            zoom=5.7,
            center={"lat": 38.5, "lon": 23.7},
            hover_name="REGION",
            hover_data={
                "Total_Stores": True,
                "Decluttered_Stores": True,
                "Coverage %": ":.1f%",
                "lat": False,
                "lon": False
            },
            mapbox_style="carto-darkmatter"
        )

        fig_map.update_layout(
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font=dict(color='white'),
            height=550,
            margin=dict(l=10, r=10, t=20, b=10)
        )

        st.plotly_chart(fig_map, use_container_width=True, config={'scrollZoom': True})
    else:
        st.info("Δεν υπάρχουν δεδομένα με έγκυρη περιοχή για τα επιλεγμένα φίλτρα.")

st.markdown("---")
