import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# ---------------------------------------------------------
# 1. ΡΥΘΜΙΣΗ ΣΕΛΙΔΑΣ & DESIGN (LOOKER THEME)
# ---------------------------------------------------------
st.set_page_config(
    page_title="DECLUTTERING QUESTION",
    layout="wide",
    page_icon="📊"
)

st.markdown("""
    <style>
    .stApp { background-color: #f4f6f8; }
    div[data-baseweb="select"] > div { background-color: #246068 !important; color: white !important; }
    .stMetric { background-color: #ffffff; padding: 15px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.05); }
    </style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# 2. ΑΣΦΑΛΕΙΑ ΜΕ ΚΩΔΙΚΟ (PASSWORD)
# ---------------------------------------------------------
def check_password():
    if "password_correct" not in st.session_state:
        st.session_state["password_correct"] = False

    if st.session_state["password_correct"]:
        return True

    st.title("🔒 Περιοχή Πρόσβασης Πελάτη")
    st.write("Please insert the password.")
    
    password_input = st.text_input("Password:", type="password")
    
    if st.button("Connect"):
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
# 3. ΦΟΡΤΩΣΗ ΔΕΔΟΜΕΝΩΝ ΑΠΟ GOOGLE SHEET
# ---------------------------------------------------------
SHEET_ID = "1Aw83hnkXT8yaXkKbpVAiCTx7AXT0Z-GXgAwS6r1itNs"

@st.cache_data(ttl=60)
def load_sheet_data(worksheet_name):
    url = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet={worksheet_name}"
    df = pd.read_csv(url)
    df.columns = [str(c).strip() for c in df.columns]
    return df

try:
    df_opap = load_sheet_data("OPAP ΕΡΩΤΗΣΗ 2000")
    df_stores = load_sheet_data("STORE STATUS (WEEKLY)")
except Exception as e:
    st.error(f"Error loading Google Sheet: {e}")
    st.stop()

# ---------------------------------------------------------
# 4. SIDEBAR - ΦΙΛΤΡΑ (WEEK & MONTH)
# ---------------------------------------------------------
st.sidebar.header("🎯 Filters")

# Φίλτρο Μήνα (DATE/MONTH)
if "DATE" in df_opap.columns:
    df_opap["MONTH"] = pd.to_datetime(df_opap["DATE"], errors='coerce').dt.strftime('%B %Y')
    available_months = ["ALL"] + list(df_opap["MONTH"].dropna().unique())
else:
    available_months = ["ALL"]

selected_month = st.sidebar.selectbox("MONTH (Μήνας)", available_months)

df_filtered = df_opap.copy()
if selected_month != "ALL":
    df_filtered = df_filtered[df_filtered["MONTH"] == selected_month]

# Φίλτρο Εβδομάδας (WEEK)
if "WEEK" in df_filtered.columns:
    available_weeks = ["ALL"] + sorted(list(df_filtered["WEEK"].dropna().unique()))
else:
    available_weeks = ["ALL"]

selected_week = st.sidebar.selectbox("WEEK (Εβδομάδα)", available_weeks)

if selected_week != "ALL":
    df_filtered = df_filtered[df_filtered["WEEK"] == selected_week]

# ---------------------------------------------------------
# 5. DASHBOARD MAIN CONTENT
# ---------------------------------------------------------
st.title("📊 Allwyn Decluttering Dashboard")
st.markdown("---")

# ---------------------------------------------------------
# ΔΙΑΓΡΑΜΜΑ 2: NETWORK COVERAGE
# ---------------------------------------------------------
st.subheader("NETWORK COVERAGE")

if not df_filtered.empty:
    # 1. Υπολογισμός Τελευταίας Επίσκεψης ανά ID
    if "AA" in df_filtered.columns:
        df_sorted = df_filtered.sort_values(by="AA", ascending=False)
    else:
        df_sorted = df_filtered.copy()

    df_last_visit = df_sorted.drop_duplicates(subset=["ID"], keep="first").copy()

    # 2. Υπολογισμός ACTIVE καταστημάτων
    df_stores_filtered = df_stores.copy()
    if selected_week != "ALL" and "WEEK" in df_stores.columns:
        df_stores_filtered = df_stores_filtered[df_stores_filtered["WEEK"] == selected_week]

    if "ACTIVITY" in df_stores_filtered.columns:
        total_active_ids = len(df_stores_filtered[df_stores_filtered["ACTIVITY"].astype(str).str.upper() == "ACTIVE"]["ID"].unique())
    else:
        total_active_ids = len(df_last_visit[df_last_visit["STATUS"].astype(str).str.upper() == "ACTIVE"]["ID"].unique())

    if total_active_ids == 0:
        total_active_ids = len(df_last_visit["ID"].unique())

    # 3. Υπολογισμός DECLUTTERED
    valid_answers = ["ΝΑΙ", "ΔΕΝ ΥΠΗΡΧΕ ΠΑΛΑΙΟ-ΜΗ ΕΓΚΕΚΡΙΜΕΝΟ ΥΛΙΚΟ"]
    
    df_decluttered = df_last_visit[
        (df_last_visit["STATUS"].astype(str).str.upper() == "ACTIVE") & 
        (df_last_visit["ANSWER"].isin(valid_answers))
    ]
    
    decluttered_count = len(df_decluttered["ID"].unique())
    remaining_active = max(0, total_active_ids - decluttered_count)
    coverage_pct = (decluttered_count / total_active_ids * 100) if total_active_ids > 0 else 0

    # Κάρτες Μετρικών
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
        textposition='inside'
    ))

    fig_coverage.add_trace(go.Bar(
        y=["Network Coverage"],
        x=[remaining_active],
        name="Remaining",
        orientation='h',
        marker=dict(color='#1B4D54'),
        text=f"Total: {total_active_ids:,}",
        textposition='outside'
    ))

    fig_coverage.update_layout(
        barmode='stack',
        height=180,
        margin=dict(l=20, r=20, t=30, b=20),
        xaxis=dict(range=[0, max(total_active_ids * 1.15, 100)], title="Total Active IDs"), # Διορθώθηκε το typo εδώ
        showlegend=True,
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )

    st.plotly_chart(fig_coverage, use_container_width=True)

st.markdown("---")

# ---------------------------------------------------------
# ΔΙΑΓΡΑΜΜΑ 1: ΑΦΑΙΡΕΘΗΚΕ ΤΥΧΟΝ ΤΟΠΟΘΕΤΗΜΕΝΟ ΥΛΙΚΟ
# ---------------------------------------------------------
st.subheader("ΑΦΑΙΡΕΘΗΚΕ ΤΥΧΟΝ ΤΟΠΟΘΕΤΗΜΕΝΟ ΠΑΛΑΙΟ Η ΜΗ ΕΓΚΡΚΡΙΜΕΝΟ ΥΛΙΚΟ (ΑΦΙΣΕΣ) ΑΠΟ ΤΟ ΚΑΤΑΣΤΗΜΑ ?")

if "WEEK" in df_filtered.columns and "ANSWER" in df_filtered.columns:
    df_chart = df_filtered.groupby(["WEEK", "ANSWER"]).size().reset_index(name="Count")
    
    color_map = {
        "ΝΑΙ": "#2EE6B6",
        "ΔΕΝ ΥΠΗΡΧΕ ΠΑΛΑΙΟ-ΜΗ ΕΓΚΕΚΡΙΜΕΝΟ ΥΛΙΚΟ": "#178A8E",
        "ΟΧΙ": "#0F3843"
    }

    fig_weekly = px.bar(
        df_chart,
        x="WEEK",
        y="Count",
        color="ANSWER",
        color_discrete_map=color_map,
        text_auto=True
    )

    fig_weekly.update_layout(
        barmode='stack',
        xaxis_title="Week",
        yaxis_title="Total Answers",
        legend_title_text="",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        height=450
    )

    st.plotly_chart(fig_weekly, use_container_width=True)

# ---------------------------------------------------------
# 6. ΑΝΑΛΥΤΙΚΟΣ ΠΙΝΑΚΑΣ ΔΕΔΟΜΕΝΩΝ
# ---------------------------------------------------------
with st.expander("🔍 Search & IDs"):
    st.dataframe(df_filtered, use_container_width=True)
