"""CRIS Analysis Page.

Main investigative interface with chat, profile cards, and link analysis.
"""

import streamlit as st
from ui.components.chat_interface import render_chat_interface

st.title("🔍 Investigative Analysis")

if "current_case" not in st.session_state:
    st.warning("Please select a case from the Cases page to begin deep analysis.")
    if st.button("Go to Cases"):
        st.switch_page("ui/pages/cases.py")
    st.stop()

case_id = st.session_state.current_case
st.subheader(f"Analyzing: {case_id}")

# Left: Chat Interface
# Right: Contextual Insights (Profile, Links, etc)
chat_col, insight_col = st.columns([2, 1])

with chat_col:
    render_chat_interface()

with insight_col:
    st.subheader("👤 Key Profiles")
    with st.container(border=True):
        st.markdown("**Suspect: 'Unknown Male'**")
        st.progress(0.75, text="Profile Confidence")
        st.caption("Organized, Marauder behavior, Local knowledge.")
        st.button("View Full Profile", key="prof1")
        
    st.divider()
    
    st.subheader("🔗 Strongest Links")
    with st.container(border=True):
        st.markdown("**CASE-2023-104** (92% MO Match)")
        st.markdown("**CASE-2024-005** (Common Witness)")
        st.button("Compare Cases")
        
    st.divider()
    
    st.subheader("🖼️ Related Evidence")
    # Mock evidence gallery
    cols = st.columns(2)
    cols[0].image("https://via.placeholder.com/150", caption="CCTV Frame")
    cols[1].image("https://via.placeholder.com/150", caption="Physical Evidence")
