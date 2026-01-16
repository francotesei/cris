"""Case Data Models.

Defines the structures for criminal cases, including status, crime types,
and summary information.
"""

from datetime import datetime
from enum import Enum
from typing import List, Optional
from pydantic import BaseModel, Field, ConfigDict


class CaseStatus(str, Enum):
    """Possible statuses for a criminal case."""
    OPEN = "open"
    CLOSED = "closed"
    COLD = "cold"
    PENDING = "pending"


class CrimeType(str, Enum):
    """Common types of crimes supported by CRIS."""
    HOMICIDE = "homicide"
    ROBBERY = "robbery"
    ASSAULT = "assault"
    BURGLARY = "burglary"
    THEFT = "theft"
    FRAUD = "fraud"
    NARCOTICS = "narcotics"
    SEX_CRIME = "sex_crime"
    KIDNAPPING = "kidnapping"
    ARSON = "arson"
    CYBERCRIME = "cybercrime"
    OTHER = "other"


class CaseBase(BaseModel):
    """Base case model with shared fields."""
    title: str = Field(..., min_length=5, max_length=200)
    description: str
    status: CaseStatus = CaseStatus.OPEN
    crime_type: CrimeType = CrimeType.OTHER
    date_occurred: datetime
    jurisdiction: str
    priority: int = Field(default=3, ge=1, le=5)
    
    model_config = ConfigDict(from_attributes=True)


class CaseCreate(CaseBase):
    """Model for creating a new case."""
    pass


class CaseUpdate(BaseModel):
    """Model for updating an existing case."""
    title: Optional[str] = None
    description: Optional[str] = None
    status: Optional[CaseStatus] = None
    crime_type: Optional[CrimeType] = None
    date_occurred: Optional[datetime] = None
    jurisdiction: Optional[str] = None
    priority: Optional[int] = None


class Case(CaseBase):
    """Full case model including system-generated fields."""
    id: str
    date_reported: datetime = Field(default_factory=datetime.now)
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)


class CaseSummary(BaseModel):
    """Brief summary of a case for list views."""
    id: str
    title: str
    status: CaseStatus
    crime_type: CrimeType
    date_occurred: datetime
    priority: int
