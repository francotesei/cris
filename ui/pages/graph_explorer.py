"""CRIS Graph Explorer Page.

Interactive exploration of the Neo4j knowledge graph.
"""

import streamlit as st
from ui.components.graph_viewer import render_graph_viewer

st.title("🕸️ Knowledge Graph Explorer")

col_sidebar, col_main = st.columns([1, 3])

with col_sidebar:
    st.subheader("Filters")
    st.multiselect("Node Types", ["Case", "Person", "Location", "Evidence", "Event"], default=["Case", "Person"])
    st.multiselect("Relationship Types", ["SUSPECT_IN", "KNOWS", "WORKS_AT"], default=["SUSPECT_IN"])
    
    st.divider()
    st.subheader("Path Finder")
    st.text_input("Start Node ID")
    st.text_input("End Node ID")
    st.slider("Max Depth", 1, 10, 6)
    st.button("Find Connections", type="primary")

with col_main:
    st.info("Interactive visualization of investigative connections. Use mouse to zoom/drag.")
    # In a real implementation, this would fetch data from Neo4j
    render_graph_viewer()
    
    st.divider()
    st.subheader("Node Details")
    st.write("Click a node in the graph to see its detailed properties and chain of custody.")
