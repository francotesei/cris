"""Map Viewer Component.

Visualizes geospatial data using Folium in Streamlit.
"""

import streamlit as st
from streamlit_folium import st_folium
import folium
from folium.plugins import HeatMap

def render_map_viewer(df=None, center=[40.7128, -74.0060], zoom=12):
    """Render an interactive map with markers and heatmap."""
    
    m = folium.Map(location=center, zoom_start=zoom)
    
    if df is not None:
        # Add markers
        for idx, row in df.iterrows():
            folium.Marker(
                [row['lat'], row['lon']],
                popup=row['type'],
                tooltip=row['type']
            ).add_to(m)
            
        # Add heatmap layer
        heat_data = [[row['lat'], row['lon']] for idx, row in df.iterrows()]
        HeatMap(heat_data).add_to(m)
        
    st_folium(m, width=700, height=500)
