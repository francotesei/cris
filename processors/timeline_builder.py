"""Timeline Builder Processor.

Constructs chronological sequences of events from witness statements and reports.
"""

from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel

from core.base_processor import BaseProcessor
from core.registry import ComponentRegistry


class TimelineEvent(BaseModel):
    """A single event in a case timeline."""
    timestamp: datetime
    description: str
    source: str
    confidence: float
    location_id: Optional[str] = None


@ComponentRegistry.register_processor("timeline_builder")
class TimelineBuilder(BaseProcessor):
    """Processor that sorts and structures events into a case timeline."""
    
    name = "timeline_builder"
    
    async def process(self, events: List[Dict[str, Any]], **kwargs: Any) -> List[TimelineEvent]:
        """Sort and validate events to build a chronological timeline."""
        self.logger.info(f"Building timeline from {len(events)} events")
        
        structured_events = []
        for e in events:
            try:
                # Handle different timestamp formats
                ts = e.get("timestamp")
                if isinstance(ts, str):
                    ts = datetime.fromisoformat(ts.replace("Z", "+00:00"))
                
                structured_events.append(TimelineEvent(
                    timestamp=ts,
                    description=e.get("description", ""),
                    source=e.get("source", "Unknown"),
                    confidence=e.get("confidence", 1.0),
                    location_id=e.get("location_id")
                ))
            except Exception as ex:
                self.logger.warning(f"Skipping malformed event: {str(ex)}")

        # Sort by timestamp
        structured_events.sort(key=lambda x: x.timestamp)
        return structured_events

    def get_supported_formats(self) -> List[str]:
        return ["json", "list"]
