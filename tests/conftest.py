"""Pytest Configuration and Fixtures.

This module contains shared fixtures and configuration for the CRIS test suite.
"""

import asyncio
from collections.abc import AsyncGenerator, Generator
from typing import Any
from unittest.mock import AsyncMock, MagicMock

import pytest

from config.settings import Settings


@pytest.fixture(scope="session")
def event_loop() -> Generator[asyncio.AbstractEventLoop, None, None]:
    """Create an event loop for async tests."""
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
def test_settings() -> Settings:
    """Create test settings with mock values."""
    return Settings(
        llm_provider="gemini",
        google_api_key="test_key",
        neo4j_uri="bolt://localhost:7687",
        neo4j_user="neo4j",
        neo4j_password="testpassword",
        chroma_persist_dir="./test_data/chroma",
        debug=True,
        log_level="DEBUG",
    )


@pytest.fixture
def mock_llm_service() -> MagicMock:
    """Create a mock LLM service."""
    mock = MagicMock()
    mock.generate = AsyncMock(return_value="Mock LLM response")
    mock.generate_structured = AsyncMock(return_value={})
    return mock


@pytest.fixture
def mock_neo4j_client() -> MagicMock:
    """Create a mock Neo4j client."""
    mock = MagicMock()
    mock.execute_query = AsyncMock(return_value=[])
    mock.create_node = AsyncMock(return_value={"id": "test_id"})
    mock.create_relationship = AsyncMock(return_value=True)
    return mock


@pytest.fixture
def mock_vector_store() -> MagicMock:
    """Create a mock vector store."""
    mock = MagicMock()
    mock.add_documents = AsyncMock(return_value=["doc_1", "doc_2"])
    mock.search = AsyncMock(return_value=[])
    return mock


@pytest.fixture
def sample_case_data() -> dict[str, Any]:
    """Create sample case data for testing."""
    return {
        "id": "CASE-2024-001",
        "title": "Test Case",
        "description": "A test case for unit testing",
        "status": "open",
        "crime_type": "robbery",
        "date_occurred": "2024-01-15T10:30:00",
        "date_reported": "2024-01-15T11:00:00",
        "jurisdiction": "Test District",
        "priority": 3,
    }


@pytest.fixture
def sample_person_data() -> dict[str, Any]:
    """Create sample person data for testing."""
    return {
        "id": "PERSON-001",
        "name": "John Doe",
        "alias": ["JD", "Johnny"],
        "date_of_birth": "1985-06-15",
        "gender": "male",
        "description": "Test person description",
        "criminal_history": False,
        "risk_score": 0.3,
    }


@pytest.fixture
def sample_evidence_data() -> dict[str, Any]:
    """Create sample evidence data for testing."""
    return {
        "id": "EVIDENCE-001",
        "type": "document",
        "description": "Test evidence document",
        "file_path": "/path/to/evidence.pdf",
        "extracted_text": "Sample extracted text from document",
        "chain_of_custody": ["Officer A", "Lab B"],
    }
