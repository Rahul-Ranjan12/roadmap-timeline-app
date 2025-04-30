import streamlit as st
import pandas as pd
import plotly.express as px
from urllib.parse import urlparse, parse_qs

# ——— Streamlit page setup ———
st.set_page_config(page_title="Roadmap Gantt", layout="wide")
st.title("📊 Roadmap Gantt Chart Viewer")

# ——— Load data from Google Sheets ———
@st.cache_data(ttl=300)
def load_data():
    sheet_url = st.secrets["sheet_url"].strip()
    parsed    = urlparse(sheet_url)
    sheet_id  = parsed.path.split("/")[3]
    gid       = parse_qs(parsed.query).get("gid", ["0"])[0]
    csv_url   = f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv&gid={gid}"

    df = pd.read_csv(
        csv_url,
        header=0,
        skip_blank_lines=True,
        on_bad_lines="skip",
    )
    # normalize headers
    df.columns = df.columns.astype(str).str.strip()

    # parse dates
    df["Start Date"] = pd.to_datetime(df["Start Date"], errors="coerce")
    df["Due Date"]   = pd.to_datetime(df["Due Date"],   errors="coerce")
    return df

df = load_data()
if df is None or df.empty or "Strategy Name" not in df.columns:
    st.error("🚨 Data load failed — please check your sheet and column headers.")
    st.stop()

# ——— Sidebar filters ———
with st.sidebar:
    st.subheader("🔍 Filters")
    strategies = st.multiselect("Strategy",      df["Strategy Name"].dropna().unique())
    priorities = st.multiselect("Priority",      df["Project Priority"].dropna().unique())
    tribes     = st.multiselect("Tribe",         df["Tribe"].dropna().unique())
    squads     = st.multiselect("Squad",         df["Squad"].dropna().unique())
    status     = st.multiselect("Status",        df["Status"].dropna().unique())
    stages     = st.multiselect("Milestone Stage", df["Milestone Stage"].dropna().unique())

# ——— Apply filters ———
filtered = df.copy()
if strategies: filtered = filtered[filtered["Strategy Name"].isin(strategies)]
if priorities: filtered = filtered[filtered["Project Priority"].isin(priorities)]
if tribes:     filtered = filtered[filtered["Tribe"].isin(tribes)]
if squads:     filtered = filtered[filtered["Squad"].isin(squads)]
if status:     filtered = filtered[filtered["Status"].isin(status)]
if stages:     filtered = filtered[filtered["Milestone Stage"].isin(stages)]

# ——— Prepare a “Task” label for each milestone ———
filtered["Task"] = filtered["Project Name"] + " ▸ " + filtered["Milestone"]

# ——— Build the Gantt chart ———
color_map = {"Red": "red", "Yellow": "yellow", "Green": "green"}

fig = px.timeline(
    filtered,
    x_start="Start Date",
    x_end="Due Date",
    y="Task",
    color="Status",
    color_discrete_map=color_map,
    hover_data=[
        "Strategy Name",
        "Tribe",
        "Squad",
        "KRs",
        "Milestone Stage",
        "Comments",
    ],
)

fig.update_yaxes(autorange="reversed")  # show earliest tasks at the top
fig.update_layout(
    title="🗓️ Milestone Gantt Chart",
    xaxis_title="Timeline",
    yaxis_title="Project ▸ Milestone",
    height=600,
    bargap=0.2,
)

# ——— Render ———
st.plotly_chart(fig, use_container_width=True)
