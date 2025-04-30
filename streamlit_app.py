import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Roadmap Timeline", layout="wide")
st.title("📊 Roadmap Timeline Viewer")

# --- Load data from Google Sheet (published as CSV) ---
@st.cache_data(ttl=300)
def load_data():
    sheet_url = st.secrets["sheet_url"]
    csv_url = sheet_url.replace("/edit#gid=", "/export?format=csv&gid=")
    
    st.write("📎 CSV URL being used:", csv_url)
    
    try:
        df = pd.read_csv(csv_url)
        st.write("✅ CSV loaded successfully!")
        st.write("🧾 Columns found:", df.columns.tolist())
        st.write("🔍 First few rows:")
        st.dataframe(df.head())
        return df
    except Exception as e:
        st.error(f"❌ Error loading CSV: {e}")
        raise

df = load_data()

# --- Filters ---
strategies = st.multiselect("Filter by Strategy", df["Strategy Name"].unique())
priority = st.multiselect("Filter by Priority", df["Project Priority"].dropna().unique())
if strategies:
    df = df[df["Strategy Name"].isin(strategies)]
if priority:
    df = df[df["Project Priority"].isin(priority)]

# --- Timeline Chart ---
fig = px.timeline(
    df,
    x_start="Start Date",
    x_end="Due Date",
    y="Milestone",
    color="Status",
    hover_data=["Project Name", "Tribe", "Squad", "KRs", "Milestone Stage", "Comments"]
)
fig.update_yaxes(autorange="reversed")  # Gantt style
fig.update_layout(title="Timeline View", height=600)
st.plotly_chart(fig, use_container_width=True)
