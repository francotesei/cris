"""Main Streamlit Entry Point.

Configures the page layout, navigation, and global state for CRIS.
"""

import streamlit as st

from config.settings import get_settings
from utils.logger import setup_logging

# Get settings
settings = get_settings()

# Page configuration
st.set_page_config(
    page_title=settings.app_title,
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize logging
setup_logging()

# Sidebar Brand
st.sidebar.title(f"🔍 {settings.app_name}")
st.sidebar.markdown("Criminal Reasoning Intelligence")
st.sidebar.divider()

# Navigation
pages = {
    "Overview": [
        st.Page("ui/pages/dashboard.py", title="Dashboard", icon="📊"),
    ],
    "Management": [
        st.Page("ui/pages/cases.py", title="Cases", icon="📁"),
    ],
    "Intelligence": [
        st.Page("ui/pages/analysis.py", title="Analysis", icon="🔍"),
        st.Page("ui/pages/predictions.py", title="Predictions", icon="🎯"),
        st.Page("ui/pages/graph_explorer.py", title="Graph Explorer", icon="🕸️"),
    ],
}

pg = st.navigation(pages)
pg.run()

# Sidebar Footer
st.sidebar.divider()
st.sidebar.caption(f"v{settings.app_version}")
st.sidebar.caption("Built for Justice with ❤️")
