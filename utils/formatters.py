"""CRIS Formatting Utilities.

Provides common formatting functions for dates, confidence scores,
and JSON outputs.
"""

import json
from datetime import datetime
from typing import Any, Optional


def format_datetime(dt: datetime | str | None) -> str:
    """Format a datetime object or ISO string to a readable string.
    
    Args:
        dt: The datetime to format.
        
    Returns:
        A formatted string (e.g., "Jan 15, 2024, 10:30 PM").
    """
    if dt is None:
        return "N/A"
    
    if isinstance(dt, str):
        try:
            dt = datetime.fromisoformat(dt.replace("Z", "+00:00"))
        except ValueError:
            return dt
            
    return dt.strftime("%b %d, %Y, %I:%M %p")


def format_confidence(score: float | str | None) -> str:
    """Format a confidence score (0-1) to a percentage or label.
    
    Args:
        score: The confidence score.
        
    Returns:
        A formatted string (e.g., "High (92%)").
    """
    if score is None:
        return "Unknown"
        
    if isinstance(score, str):
        return score.capitalize()
        
    percentage = int(score * 100)
    
    if score >= 0.8:
        label = "High"
    elif score >= 0.5:
        label = "Medium"
    else:
        label = "Low"
        
    return f"{label} ({percentage}%)"


def format_json_output(data: Any, indent: int = 2) -> str:
    """Safely format data as a JSON string.
    
    Args:
        data: The data to format.
        indent: Number of spaces for indentation.
        
    Returns:
        A pretty-printed JSON string.
    """
    try:
        return json.dumps(data, indent=indent, default=str)
    except (TypeError, ValueError):
        return str(data)


def truncate_text(text: str, max_length: int = 100) -> str:
    """Truncate text to a maximum length with ellipses.
    
    Args:
        text: The text to truncate.
        max_length: The maximum allowed length.
        
    Returns:
        The truncated text.
    """
    if not text or len(text) <= max_length:
        return text
    return text[:max_length-3] + "..."
