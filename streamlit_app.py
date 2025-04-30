import streamlit as st
import pandas as pd
import plotly.express as px
from urllib.parse import urlparse, parse_qs

# --- Streamlit page setup ---
st.set_page_config(page_title="Roadmap Timeline", layout="wide")
st.title("📊 Roadmap Timeline Viewer")

@st.cache_data(ttl=300)
def load_data():
    # Read and normalize the Google Sheet URL
    sheet_url = st.secrets["sheet_url"].strip()
    parsed   = urlparse(sheet_url)
    sheet_id = parsed.path.split("/")[3]
    gid      = parse_qs(parsed.query).get("gid", ["0"])[0]
    csv_url  = f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv&gid={gid}"

    # Load as CSV
    df = pd.read_csv(csv_url, header=0, skip_blank_lines=True, on_bad_lines="skip")
    # Clean column names
    df.columns = df.columns.astype(str).str.strip()

    # Parse date columns
    df["Start Date"] = pd.to_datetime(df["Start Date"], errors="coerce")
    df["Due Date"]   = pd.to_datetime(df["Due Date"],   errors="coerce")

    return df

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

# --- Timeline chart with exact status colors ---
fig = px.timeline(
    df,
    x_start="Start Date",
    x_end="Due Date",
    y="Milestone",
    color="Status",
    color_discrete_map={
        "Red":    "red",
        "Yellow": "yellow",
        "Green":  "green",
    },
    hover_data=[
        "Strategy Name",
        "Project Name",
        "Tribe",
        "Squad",
        "KRs",
        "Milestone Stage",
        "Comments",
    ],
)

fig.update_yaxes(autorange="reversed")  # Gantt-style ordering
fig.update_layout(
    title="🗓️ Milestone Timeline",
    height=600,
    legend_title_text="Status"
)

st.plotly_chart(fig, use_container_width=True)
