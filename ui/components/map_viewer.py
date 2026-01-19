"""Map Viewer Component.

Visualizes geospatial data using Folium in Streamlit.
"""

from typing import List, Optional

import streamlit as st
from streamlit_folium import st_folium
import folium
from folium.plugins import HeatMap

from config.settings import get_settings


def render_map_viewer(df=None, center: Optional[List[float]] = None, zoom: Optional[int] = None):
    """Render an interactive map with markers and heatmap.
    
    Args:
        df: DataFrame with 'lat', 'lon', and 'type' columns.
        center: Map center as [lat, lon]. Defaults to settings.
        zoom: Initial zoom level. Defaults to settings.
    """
    settings = get_settings()
    
    # Use settings defaults if not provided
    if center is None:
        center = [settings.default_map_center_lat, settings.default_map_center_lon]
    if zoom is None:
        zoom = settings.default_map_zoom
    
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
