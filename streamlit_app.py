import streamlit as st
import pandas as pd
import plotly.express as px
from urllib.parse import urlparse, parse_qs

# --- Streamlit page setup ---
st.set_page_config(page_title="Roadmap Timeline", layout="wide")
st.title("📊 Roadmap Timeline Viewer")

@st.cache_data(ttl=300)
def load_data():
    # 1. Read the raw sheet URL from secrets
    sheet_url = st.secrets["sheet_url"].strip()
    st.write("📎 Raw sheet URL:", sheet_url)

    # 2. Strip off any fragment (#...) and parse out the sheet ID + gid
    parsed = urlparse(sheet_url)
    base_path = parsed.path  # e.g. "/spreadsheets/d/<ID>/edit"
    sheet_id = base_path.split("/")[3]
    gid = parse_qs(parsed.query).get("gid", ["0"])[0]

    # 3. Build the proper CSV-export URL
    csv_url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv&gid={gid}"
    st.write("📎 CSV URL being used:", csv_url)

    try:
        # 4. Fetch as CSV
        df = pd.read_csv(csv_url, skip_blank_lines=True, on_bad_lines="skip", header=0)

        # 5. Clean up column names
        df.columns = df.columns.astype(str).str.strip()

        st.write("🧾 Columns loaded:", df.columns.tolist())
        st.dataframe(df.head())

        # 6. Parse dates
        df["Start Date"] = pd.to_datetime(df["Start Date"], errors="coerce")
        df["Due Date"]   = pd.to_datetime(df["Due Date"],   errors="coerce")

        return df

    except Exception as e:
        st.error(f"❌ Error loading CSV: {e}")
        return None

# --- Load & validate the data ---
df = load_data()
if df is None or df.empty or "Strategy Name" not in df.columns:
    st.error("🚨 Data load failed — please check your sheet and column headers.")
    st.stop()

# --- Sidebar filters ---
with st.sidebar:
    st.subheader("🔍 Filters")
    strategies = st.multiselect("Strategy", df["Strategy Name"].dropna().unique())
    priorities = st.multiselect("Priority",  df["Project Priority"].dropna().unique())
    tribes     = st.multiselect("Tribe",     df["Tribe"].dropna().unique())
    squads     = st.multiselect("Squad",     df["Squad"].dropna().unique())
    status     = st.multiselect("Status",    df["Status"].dropna().unique())
    stages     = st.multiselect("Milestone Stage", df["Milestone Stage"].dropna().unique())

# --- Apply filters ---
if strategies: df = df[df["Strategy Name"].isin(strategies)]
if priorities: df = df[df["Project Priority"].isin(priorities)]
if tribes:     df = df[df["Tribe"].isin(tribes)]
if squads:     df = df[df["Squad"].isin(squads)]
if status:     df = df[df["Status"].isin(status)]
if stages:     df = df[df["Milestone Stage"].isin(stages)]

# --- Timeline chart ---
fig = px.timeline(
    df,
    x_start="Start Date",
    x_end="Due Date",
    y="Milestone",
    color="Status",
    hover_data=["Strategy Name","Project Name","Tribe","Squad","KRs",
                "Milestone Stage","Comments"],
)
fig.update_yaxes(autorange="reversed")
fig.update_layout(title="🗓️ Milestone Timeline", height=600)

st.plotly_chart(fig, use_container_width=True)
