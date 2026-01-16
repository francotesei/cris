"""Evidence Data Models.

Defines the structures for physical, digital, and documentary evidence.
"""

from datetime import datetime
from enum import Enum
from typing import List, Optional
from pydantic import BaseModel, Field, ConfigDict


class EvidenceType(str, Enum):
    """Types of evidence supported by CRIS."""
    DOCUMENT = "document"
    PHOTO = "photo"
    VIDEO = "video"
    AUDIO = "audio"
    PHYSICAL = "physical"
    DIGITAL = "digital"
    FORENSIC = "forensic"
    TESTIMONY = "testimony"
    OTHER = "other"


class EvidenceBase(BaseModel):
    """Base evidence model with shared fields."""
    type: EvidenceType
    description: str
    file_path: Optional[str] = None
    chain_of_custody: List[str] = []
    
    model_config = ConfigDict(from_attributes=True)


class EvidenceCreate(EvidenceBase):
    """Model for creating new evidence."""
    extracted_text: Optional[str] = None


class Evidence(EvidenceBase):
    """Full evidence model including system-generated fields."""
    id: str
    extracted_text: Optional[str] = None
    embedding_id: Optional[str] = None
    case_id: str
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
