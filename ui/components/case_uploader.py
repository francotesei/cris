"""Case Uploader Component.

Provides a file upload interface for investigative documents.
"""

import streamlit as st
from typing import List

def render_case_uploader() -> List[st.runtime.uploaded_file_manager.UploadedFile]:
    """Render the file uploader widget.
    
    Returns:
        List of uploaded file objects.
    """
    uploaded_files = st.file_uploader(
        "Upload Case Files",
        type=["pdf", "jpg", "jpeg", "png", "txt", "md"],
        accept_multiple_files=True,
        help="Support for reports, statements, and evidence photos."
    )
    
    if uploaded_files:
        st.success(f"{len(uploaded_files)} files staged for processing.")
        
    return uploaded_files or []
