"""CRIS Models Module.

This module contains Pydantic models for data validation
and serialization throughout the CRIS system.
"""

from models.case import Case, CaseStatus, CrimeType, CaseCreate, CaseSummary
from models.person import Person, PersonRole, PersonCreate, Relationship
from models.evidence import Evidence, EvidenceType, EvidenceCreate
from models.prediction import Prediction, PredictionType, PredictionCreate

__all__ = [
    # Case models
    "Case",
    "CaseStatus",
    "CrimeType",
    "CaseCreate",
    "CaseSummary",
    # Person models
    "Person",
    "PersonRole",
    "PersonCreate",
    "Relationship",
    # Evidence models
    "Evidence",
    "EvidenceType",
    "EvidenceCreate",
    # Prediction models
    "Prediction",
    "PredictionType",
    "PredictionCreate",
]
