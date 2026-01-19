"""CRIS Dashboard Page.

Provides a high-level overview of active cases, crime hotspots, and system alerts.
"""

import streamlit as st
import pandas as pd
import plotly.express as px
from pathlib import Path

from ui.components.map_viewer import render_map_viewer

# Header with logo
header_col1, header_col2 = st.columns([1, 4])
with header_col1:
    icon_path = Path(__file__).parent.parent.parent / "assets" / "cris_icon.svg"
    if icon_path.exists():
        st.image(str(icon_path), width=80)
        
with header_col2:
    st.title("Investigative Dashboard")
    st.caption("Real-time criminal intelligence overview")

# Top Stats
col1, col2, col3, col4 = st.columns(4)
col1.metric("Active Cases", "12", "+2")
col2.metric("Solve Rate", "68%", "5%")
col3.metric("High Risk Suspects", "5", "0")
col4.metric("Pending Alerts", "3", "-1")

st.divider()

# Main Layout
m_col1, m_col2 = st.columns([2, 1])

with m_col1:
    st.subheader("📍 Crime Hotspots")
    # Sample data for map
    sample_data = pd.DataFrame({
        'lat': [40.7128, 40.7200, 40.7300],
        'lon': [-74.0060, -74.0100, -74.0200],
        'type': ['Robbery', 'Burglary', 'Assault']
    })
    render_map_viewer(sample_data)

with m_col2:
    st.subheader("🔔 Intelligence Alerts")
    with st.container(border=True):
        st.warning("**Case Connection Detected**\nMO match between CASE-2024-001 and CASE-2024-012.")
        st.info("**Prediction Update**\nIncreased risk of robbery in Sector B during next 48h.")
        st.error("**New High-Risk Entity**\nSuspect ID 'JD-99' identified in social media patterns.")

st.divider()

# Recent Cases Table
st.subheader("📁 Recent Cases")
cases_data = {
    "ID": ["CASE-2024-001", "CASE-2024-002", "CASE-2024-003"],
    "Title": ["Robbery at Main St", "Missing Person - Sarah L", "Cyber Fraud Series"],
    "Status": ["Open", "In-Progress", "Closed"],
    "Priority": ["High", "Medium", "Low"],
    "Last Updated": ["2024-01-15", "2024-01-14", "2024-01-12"]
}
st.table(pd.DataFrame(cases_data))
