"""Person Data Models.

Defines the structures for victims, suspects, witnesses, and other persons
of interest involved in a case.
"""

from datetime import date, datetime
from enum import Enum
from typing import List, Optional
from pydantic import BaseModel, Field, ConfigDict


class PersonRole(str, Enum):
    """Roles a person can have in a case."""
    VICTIM = "victim"
    SUSPECT = "suspect"
    WITNESS = "witness"
    PERSON_OF_INTEREST = "person_of_interest"
    INFORMANT = "informant"
    LEGAL_REP = "legal_rep"
    OFFICER = "officer"


class RelationshipType(str, Enum):
    """Types of relationships between people."""
    KNOWS = "knows"
    RELATED_TO = "related_to"
    WORKS_WITH = "works_with"
    LIVES_WITH = "lives_with"
    ENEMIES = "enemies"
    PARTNERS = "partners"
    UNKNOWN = "unknown"


class PersonBase(BaseModel):
    """Base person model with shared fields."""
    name: str
    alias: List[str] = []
    date_of_birth: Optional[date] = None
    gender: Optional[str] = None
    description: Optional[str] = None
    criminal_history: bool = False
    
    model_config = ConfigDict(from_attributes=True)


class PersonCreate(PersonBase):
    """Model for creating a new person."""
    pass


class Person(PersonBase):
    """Full person model including system-generated fields."""
    id: str
    risk_score: float = Field(default=0.0, ge=0.0, le=1.0)
    created_at: datetime = Field(default_factory=datetime.now)


class Relationship(BaseModel):
    """Model for relationships between two people."""
    person1_id: str
    person2_id: str
    type: RelationshipType
    description: Optional[str] = None
    since: Optional[date] = None
    confirmed: bool = True
