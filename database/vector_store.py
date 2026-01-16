"""ChromaDB Vector Store.

Implementation of BaseVectorStore using ChromaDB for semantic search.
"""

from typing import Any, Dict, List, Optional

import chromadb
from chromadb.config import Settings as ChromaSettings

from core.base_vector_store import BaseVectorStore
from config.settings import get_settings


class VectorStore(BaseVectorStore):
    """Vector database implementation using ChromaDB."""
    
    def __init__(self, persist_dir: str = None) -> None:
        """Initialize the ChromaDB client."""
        settings = get_settings()
        self.persist_dir = persist_dir or settings.chroma_persist_dir
        
        self.client = chromadb.PersistentClient(
            path=self.persist_dir,
            settings=ChromaSettings(allow_reset=True)
        )
        # Default collection for evidence
        self.collection = self.client.get_or_create_collection(name="evidence")
        super().__init__(persist_dir=self.persist_dir)

    async def add_documents(self, documents: List[str], metadatas: Optional[List[Dict[str, Any]]] = None, ids: Optional[List[str]] = None) -> List[str]:
        """Add text documents to ChromaDB."""
        # Generate IDs if not provided
        if ids is None:
            ids = [f"id_{i}" for i in range(len(documents))]
            
        self.collection.add(
            documents=documents,
            metadatas=metadatas,
            ids=ids
        )
        return ids

    async def search(self, query: str, n_results: int = 5, filter: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """Query ChromaDB for similar documents."""
        results = self.collection.query(
            query_texts=[query],
            n_results=n_results,
            where=filter
        )
        
        # Format results to a consistent structure
        formatted = []
        for i in range(len(results["ids"][0])):
            formatted.append({
                "id": results["ids"][0][i],
                "document": results["documents"][0][i],
                "metadata": results["metadatas"][0][i],
                "distance": results["distances"][0][i] if results["distances"] else None
            })
        return formatted

    async def delete(self, ids: List[str]) -> bool:
        """Remove documents from the collection."""
        try:
            self.collection.delete(ids=ids)
            return True
        except Exception as e:
            self.logger.error(f"Failed to delete from ChromaDB: {str(e)}")
            return False

    def get_collection(self, name: str) -> chromadb.Collection:
        """Get or create a specific collection by name."""
        return self.client.get_or_create_collection(name=name)
