"""CRIS Cases Management Page.

Handles case creation, file uploads, and case detail views.
"""

import streamlit as st
from ui.components.case_uploader import render_case_uploader

st.title("📁 Case Management")

tabs = st.tabs(["Active Cases", "Upload New Case", "Archives"])

with tabs[0]:
    st.subheader("Current Investigations")
    # Search and Filter
    col1, col2 = st.columns([2, 1])
    col1.text_input("Search cases...", placeholder="ID, Title, or Suspect")
    col2.selectbox("Filter by Status", ["All", "Open", "Closed", "Cold"])
    
    # Simple list (Mock)
    st.info("Select a case to view details and start analysis.")
    if st.button("CASE-2024-001: Downtown Jewelry Robbery"):
        st.session_state.current_case = "CASE-2024-001"
        st.switch_page("ui/pages/analysis.py")

with tabs[1]:
    st.subheader("Process New Evidence")
    st.write("Upload investigative reports, witness statements, or photos to create a new case or update an existing one.")
    
    selected_case = st.selectbox("Assign to Case", ["New Case", "CASE-2024-001", "CASE-2024-002"])
    
    if selected_case == "New Case":
        st.text_input("Case Title")
        st.text_area("Initial Summary")
        
    render_case_uploader()
    
    if st.button("Process & Index", type="primary"):
        with st.status("Processing documents..."):
            st.write("Extracting text...")
            st.write("Running Entity Recognition...")
            st.write("Generating Graph Nodes...")
            st.success("Case indexed successfully!")

with tabs[2]:
    st.subheader("Case Archives")
    st.write("View historical cases and solved patterns.")
