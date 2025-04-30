import streamlit as st
import pandas as pd
import plotly.figure_factory as ff            # <<— import the Gantt helper
from urllib.parse import urlparse, parse_qs

# --- Streamlit page setup ---
st.set_page_config(page_title="Roadmap Timeline", layout="wide")
st.title("📊 Roadmap Gantt Chart Viewer")

@st.cache_data(ttl=300)
def load_data():
    sheet_url = st.secrets["sheet_url"].strip()
    parsed   = urlparse(sheet_url)
    sheet_id = parsed.path.split("/")[3]
    gid      = parse_qs(parsed.query).get("gid", ["0"])[0]
    csv_url  = f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv&gid={gid}"
    df = pd.read_csv(csv_url, header=0, skip_blank_lines=True, on_bad_lines="skip")
    df.columns = df.columns.astype(str).str.strip()
    df["Start Date"] = pd.to_datetime(df["Start Date"], errors="coerce")
    df["Due Date"]   = pd.to_datetime(df["Due Date"],   errors="coerce")
    return df

df = load_data()
if df is None or df.empty or "Strategy Name" not in df.columns:
    st.error("🚨 Data load failed — please check your sheet.")
    st.stop()

# Sidebar filters (unchanged)
with st.sidebar:
    st.subheader("🔍 Filters")
    strategies = st.multiselect("Strategy", df["Strategy Name"].dropna().unique())
    priorities = st.multiselect("Priority",  df["Project Priority"].dropna().unique())
    tribes     = st.multiselect("Tribe",     df["Tribe"].dropna().unique())
    squads     = st.multiselect("Squad",     df["Squad"].dropna().unique())
    status     = st.multiselect("Status",    df["Status"].dropna().unique())
    stages     = st.multiselect("Stage",     df["Milestone Stage"].dropna().unique())

for f, col in [
    (strategies, "Strategy Name"),
    (priorities,  "Project Priority"),
    (tribes,      "Tribe"),
    (squads,      "Squad"),
    (status,      "Status"),
    (stages,      "Milestone Stage"),
]:
    if f:
        df = df[df[col].isin(f)]

# --- Prepare Gantt records ---
# one task per project–milestone
df["Task"] = df["Project Name"] + " ▸ " + df["Milestone"]
gantt_records = (
    df[["Task", "Start Date", "Due Date", "Status"]]
    .rename(columns={"Start Date":"Start", "Due Date":"Finish"})
    .to_dict("records")
)

# Map status to exact colors
color_map = {"Red":"red", "Yellow":"yellow", "Green":"green"}

fig = ff.create_gantt(
    gantt_records,
    colors=color_map,
    index_col="Status",
    show_colorbar=True,
    group_tasks=True,
    title="🗓️ Milestone Gantt Chart"
)

st.plotly_chart(fig, use_container_width=True)
