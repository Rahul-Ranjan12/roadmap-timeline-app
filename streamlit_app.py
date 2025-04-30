import streamlit as st
import pandas as pd
import plotly.express as px

# --- Streamlit page setup ---
st.set_page_config(page_title="Roadmap Timeline", layout="wide")
st.title("📊 Roadmap Timeline Viewer")

# --- Load data from Google Sheet (published as CSV) ---
@st.cache_data(ttl=300)
def load_data():
    sheet_url = st.secrets["sheet_url"]
    csv_url = sheet_url.replace("/edit#gid=", "/export?format=csv&gid=")

    st.write("📎 CSV URL being used:", csv_url)

    try:
        df = pd.read_csv(csv_url, skip_blank_lines=True)

        # Ensure proper header usage
        if df.columns[0] != "Strategy Name":
            df.columns = df.iloc[0]
            df = df[1:]

        # Clean up column names (strip spaces, normalize encoding)
        df.columns = df.columns.astype(str).str.strip().str.encode('ascii', errors='ignore').str.decode()

        st.write("🧾 Normalized Columns:", df.columns.tolist())

        # Parse dates safely
        df["Start Date"] = pd.to_datetime(df["Start Date"], errors="coerce")
        df["Due Date"] = pd.to_datetime(df["Due Date"], errors="coerce")

        st.write("✅ Dataframe loaded:")
        st.dataframe(df.head())

        return df

    except Exception as e:
        st.error(f"❌ Error loading CSV: {e}")
        return None


# --- Load the data ---
df = load_data()

# --- Defensive check to avoid crashing if data failed to load ---
if df is None or df.empty or "Strategy Name" not in df.columns:
    st.error("🚨 Data could not be loaded properly. Please check your sheet and column headers.")
    st.stop()

# --- Filters ---
with st.sidebar:
    st.subheader("🔍 Filters")
    strategies = st.multiselect("Strategy", df["Strategy Name"].dropna().unique())
    priorities = st.multiselect("Priority", df["Project Priority"].dropna().unique())
    tribes = st.multiselect("Tribe", df["Tribe"].dropna().unique())
    squads = st.multiselect("Squad", df["Squad"].dropna().unique())
    status = st.multiselect("Status", df["Status"].dropna().unique())
    stages = st.multiselect("Milestone Stage", df["Milestone Stage"].dropna().unique())

# --- Apply filters ---
if strategies:
    df = df[df["Strategy Name"].isin(strategies)]
if priorities:
    df = df[df["Project Priority"].isin(priorities)]
if tribes:
    df = df[df["Tribe"].isin(tribes)]
if squads:
    df = df[df["Squad"].isin(squads)]
if status:
    df = df[df["Status"].isin(status)]
if stages:
    df = df[df["Milestone Stage"].isin(stages)]

# --- Timeline chart ---
fig = px.timeline(
    df,
    x_start="Start Date",
    x_end="Due Date",
    y="Milestone",
    color="Status",
    hover_data=["Strategy Name", "Project Name", "Tribe", "Squad", "KRs", "Milestone Stage", "Comments"]
)

fig.update_yaxes(autorange="reversed")
fig.update_layout(title="🗓️ Milestone Timeline", height=600)
st.plotly_chart(fig, use_container_width=True)
