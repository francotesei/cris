"""Graph Viewer Component.

Visualizes Neo4j graph data using PyVis in Streamlit.
"""

import streamlit as st
import streamlit.components.v1 as components
from pyvis.network import Network
import tempfile
import os

def render_graph_viewer(nodes=None, edges=None):
    """Render an interactive graph using PyVis."""
    
    # Create a dummy network if no data provided
    net = Network(height="600px", width="100%", bgcolor="#ffffff", font_color="black", notebook=False)
    
    if nodes is None:
        # Mock data
        net.add_node("C1", label="CASE-2024-001", color="#FF5733", title="Downtown Robbery")
        net.add_node("P1", label="John Doe", color="#33FF57", title="Suspect")
        net.add_node("L1", label="Main St 123", color="#3357FF", title="Crime Scene")
        net.add_edge("P1", "C1", label="SUSPECT_IN")
        net.add_edge("C1", "L1", label="OCCURRED_AT")
    else:
        # Implementation for real nodes/edges
        pass

    net.toggle_physics(True)
    
    # Save to temp file and serve
    with tempfile.NamedTemporaryFile(delete=False, suffix=".html") as tmp:
        net.save_graph(tmp.name)
        with open(tmp.name, 'r', encoding='utf-8') as f:
            html = f.read()
            components.html(html, height=650)
        os.unlink(tmp.name)
