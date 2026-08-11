import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import urllib.parse

# ---------------------------------------------------------
# 1. ΡΥΘΜΙΣΗ ΣΕΛΙΔΑΣ & DESIGN (DARK PETROL THEME)
# ---------------------------------------------------------
st.set_page_config(
    page_title="DECLUTTERING QUESTION",
    layout="wide",
    page_icon="📊"
)

st.markdown("""
    <style>
    .stApp { background-color: #112229; color: #FFFFFF; }
    div[data-baseweb="select"] > div { background-color: #1A333D !important; color: white !important; }
    .stMetric { background-color: #1A333D; padding: 15px; border-radius: 8px; border: 1px solid #2A4D59; }
    .stMetric label { color: #A3C1AD !important; }
    .stMetric div { color: #FFFFFF !important; }
    h1, h2, h3, h4, h5, h6, label, p, span { color: #FFFFFF !important; }
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
                st.error("⚠️ Wrong password.")
            
    return False

if not check_password():
    st.stop()

# ---------------------------------------------------------
# 3. ΦΟΡΤΩΣΗ & ΜΕΤΑΤΡΟΠΗ ΗΜΕΡΟΜΗΝΙΑΣ (DD/MM/YYYY)
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

# Μετατροπή ημερομηνίας
if "DATE" in df_opap.columns:
    df_opap["DATE_DT"] = pd.to_datetime(df_opap["DATE"], format="%d/%m/%Y", errors='coerce')
    df_opap["DATE_DT"] = df_opap["DATE_DT"].fillna(pd.to_datetime(df_opap["DATE"], dayfirst=True, errors='coerce'))
    df_opap["MONTH"] = df_opap["DATE_DT"].dt.strftime('%B %Y')

# Καθαρισμός στήλης WEEK
if "WEEK" in df_opap.columns:
    df_opap["WEEK_NUM"] = pd.to_numeric(df_opap["WEEK"].astype(str).str.extract(r'(\d+)')[0], errors='coerce')

# ---------------------------------------------------------
# 4. LOGOS & HEADER
# ---------------------------------------------------------
header_col1, header_col2, header_col3 = st.columns([1, 4, 1])

with header_col1:
    try:
        st.image("WEST_logo.png", width=150)
    except Exception:
        pass

with header_col2:
    st.title("📊 Allwyn Decluttering Dashboard")

with header_col3:
    try:
        st.image("ALLWYN_logo.png", width=150)
    except Exception:
        pass

st.markdown("---")

# ---------------------------------------------------------
# 5. SIDEBAR - ΦΙΛΤΡΑ
# ---------------------------------------------------------
st.sidebar.header("🎯 Filters")

# 1. Φίλτρο Μήνα
if "DATE_DT" in df_opap.columns and not df_opap["DATE_DT"].dropna().empty:
    df_months = df_opap.dropna(subset=["DATE_DT"]).sort_values("DATE_DT")
    months_order = df_months["MONTH"].unique().tolist()
else:
    months_order = sorted([x for x in df_opap["MONTH"].dropna().unique()]) if "MONTH" in df_opap.columns else []

selected_months = st.sidebar.multiselect("MONTH (Μήνας)", options=months_order, default=[])

if selected_months:
    df_month_filtered = df_opap[df_opap["MONTH"].isin(selected_months)]
else:
    df_month_filtered = df_opap.copy()

# 2. Φίλτρο Εβδομάδας
if "WEEK_NUM" in df_month_filtered.columns:
    available_weeks = sorted([int(x) for x in df_month_filtered["WEEK_NUM"].dropna().unique()])
else:
    available_weeks = []

selected_weeks = st.sidebar.multiselect("WEEK (Εβδομάδα)", options=available_weeks, default=[])

if selected_weeks:
    df_filtered = df_month_filtered[df_month_filtered["WEEK_NUM"].isin(selected_weeks)]
else:
    df_filtered = df_month_filtered.copy()

# ---------------------------------------------------------
# 6. ΔΙΑΓΡΑΜΜΑ 1: NETWORK COVERAGE (SQL LOGIC: ΗΜΕΡΟΜΗΝΙΑ / ROW ID)
# ---------------------------------------------------------
st.subheader("NETWORK COVERAGE")

if not df_filtered.empty:
    # 1. Total Active IDs
    if "ACTIVITY" in df_stores.columns:
        total_active_ids = len(df_stores[df_stores["ACTIVITY"].astype(str).str.upper() == "ACTIVE"]["ID"].unique())
    else:
        total_active_ids = len(df_opap["ID"].unique())

    # 2. Τελευταία εγγραφή ανά ID με βάση την ΗΜΕΡΟΜΗΝΙΑ (ή τη σειρά εγγραφής)
    if "DATE_DT" in df_filtered.columns and not df_filtered["DATE_DT"].isna().all():
        df_sorted = df_filtered.sort_values(by="DATE_DT")
    else:
        df_sorted = df_filtered.copy()

    # Κρατάμε την τελευταία καταγραφή για κάθε ID
    df_latest_visits = df_sorted.drop_duplicates(subset=["ID"], keep="last")

    # 3. Decluttered IDs
    valid_answers = ["ΝΑΙ", "ΔΕΝ ΥΠΗΡΧΕ ΠΑΛΑΙΟ-ΜΗ ΕΓΚΕΚΡΙΜΕΝΟ ΥΛΙΚΟ"]
    decluttered_ids = df_latest_visits[df_latest_visits["ANSWER"].isin(valid_answers)]["ID"].unique()
    
    decluttered_count = len(decluttered_ids)
    decluttered_count = min(decluttered_count, total_active_ids)
    remaining_active = max(0, total_active_ids - decluttered_count)
    coverage_pct = (decluttered_count / total_active_ids * 100) if total_active_ids > 0 else 0

    # Μετρικές
    c1, c2, c3 = st.columns(3)
    c1.metric("Total active IDs", f"{total_active_ids:,}")
    c2.metric("Decluttered", f"{decluttered_count:,}")
    c3.metric("Coverage %", f"{coverage_pct:.1f}%")

    # Stacked Horizontal Bar
    fig_coverage = go.Figure()

    fig_coverage.add_trace(go.Bar(
        y=["Network Coverage"],
        x=[decluttered_count],
        name="Decluttered",
        orientation='h',
        marker=dict(color='#20B2AA'),
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
        marker=dict(color='#1B4D54'),
        text=f"Remaining: {remaining_active:,}" if remaining_active > 0 else "",
        textposition='outside',
        textfont=dict(color='white', size=13),
        cliponaxis=False
    ))

    fig_coverage.update_layout(
        barmode='stack',
        height=180,
        margin=dict(l=20, r=120, t=30, b=20), # Αυξημένο περιθώριο δεξιά για να μην κόβεται το text
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(color='white'),
        xaxis=dict(
            range=[0, total_active_ids * 1.2], # Διευρυμένο range για τα labels
            title="Total Active IDs",
            showgrid=False,
            color='white'
        ),
        yaxis=dict(color='white'),
        showlegend=True,
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1, font=dict(color='white'))
    )

    st.plotly_chart(fig_coverage, use_container_width=True)

st.markdown("---")

# ---------------------------------------------------------
# 7. ΔΙΑΓΡΑΜΜΑ 2: WEEKLY STACKED BAR (ΑΡΙΘΜΟΙ ΑΝΑ ΧΡΩΜΑ/ΑΠΑΝΤΗΣΗ)
# ---------------------------------------------------------
st.subheader("ΑΦΑΙΡΕΘΗΚΕ ΤΥΧΟΝ ΤΟΠΟΘΕΤΗΜΕΝΟ ΠΑΛΑΙΟ Η ΜΗ ΕΓΚΡΚΡΙΜΕΝΟ ΥΛΙΚΟ (ΑΦΙΣΕΣ) ΑΠΟ ΤΟ ΚΑΤΑΣΤΗΜΑ ?")

if "WEEK_NUM" in df_filtered.columns and "ANSWER" in df_filtered.columns and not df_filtered.empty:
    df_chart = df_filtered.groupby(["WEEK_NUM", "ANSWER"]).size().reset_index(name="Count")
    df_chart = df_chart.sort_values(by="WEEK_NUM")
    df_chart["WEEK_LABEL"] = "Week " + df_chart["WEEK_NUM"].astype(int).astype(str)

    color_map = {
        "ΝΑΙ": "#2EE6B6",
        "ΔΕΝ ΥΠΗΡΧΕ ΠΑΛΑΙΟ-ΜΗ ΕΓΚΕΚΡΙΜΕΝΟ ΥΛΙΚΟ": "#178A8E",
        "ΟΧΙ": "#0F3843"
    }

    fig_weekly = px.bar(
        df_chart,
        x="WEEK_LABEL",
        y="Count",
        color="ANSWER",
        color_discrete_map=color_map,
        text="Count"
    )

    # Καθαροί αριθμοί ανά τμήμα (χωρίς σύνολα στην κορυφή)
    fig_weekly.update_traces(
        textposition='inside',
        insidetextfont=dict(color='white', size=11),
        textangle=0
    )

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
            color='white'
        )
    )

    st.plotly_chart(fig_weekly, use_container_width=True)
else:
    st.info("No data available for the selected filters.")

st.markdown("---")

# ---------------------------------------------------------
# 8. ΑΝΑΖΗΤΗΣΗ STORE ID & ΙΣΤΟΡΙΚΟ
# ---------------------------------------------------------
st.subheader("🔎 Store ID History Lookup")

if "ID" in df_opap.columns:
    all_store_ids = sorted([str(x) for x in df_opap["ID"].dropna().unique()])
    selected_store_id = st.selectbox("Select or Search Store ID:", options=["-- Choose Store ID --"] + all_store_ids)

    if selected_store_id != "-- Choose Store ID --":
        df_single_store = df_opap[df_opap["ID"].astype(str) == selected_store_id].copy()
        
        if "WEEK_NUM" in df_single_store.columns:
            df_single_store = df_single_store.sort_values(by="WEEK_NUM")
            
        st.write(f"**History for Store ID:** `{selected_store_id}`")
        display_cols = [c for c in ["WEEK", "DATE", "MONTH", "STATUS", "ANSWER"] if c in df_single_store.columns]
        st.dataframe(df_single_store[display_cols], use_container_width=True, hide_index=True)
