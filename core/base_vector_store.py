"""Base Vector Store Abstractions.

Defines the interface for semantic search and embedding storage.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional

from utils.logger import get_logger


class BaseVectorStore(ABC):
    """Abstract base class for vector databases."""
    
    def __init__(self, **kwargs: Any) -> None:
        """Initialize the vector store."""
        self.logger = get_logger("database.vector_store")
        self.config = kwargs

    @abstractmethod
    async def add_documents(self, documents: List[str], metadatas: Optional[List[Dict[str, Any]]] = None, ids: Optional[List[str]] = None) -> List[str]:
        """Add text documents to the vector store.
        
        Args:
            documents: List of text contents.
            metadatas: Optional metadata for each document.
            ids: Optional unique identifiers.
            
        Returns:
            List of generated or provided IDs.
        """
        pass

    @abstractmethod
    async def search(self, query: str, n_results: int = 5, filter: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """Perform semantic search.
        
        Args:
            query: The search query text.
            n_results: Number of results to return.
            filter: Metadata filter.
            
        Returns:
            List of matching documents with metadata and similarity scores.
        """
        pass

    @abstractmethod
    async def delete(self, ids: List[str]) -> bool:
        """Delete documents by ID.
        
        Args:
            ids: List of IDs to remove.
            
        Returns:
            True if successful.
        """
        pass
