"""Base Graph Database Abstractions.

Defines the interface for knowledge graph operations.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional


class BaseGraphDB(ABC):
    """Abstract base class for graph databases like Neo4j."""
    
    @abstractmethod
    async def execute_query(self, query: str, parameters: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """Execute a raw graph query (e.g., Cypher).
        
        Args:
            query: The query string.
            parameters: Query parameters.
            
        Returns:
            List of result records as dictionaries.
        """
        pass

    @abstractmethod
    async def create_node(self, label: str, properties: Dict[str, Any]) -> Dict[str, Any]:
        """Create a single node.
        
        Args:
            label: The node label (e.g., "Person").
            properties: Node attributes.
            
        Returns:
            The created node's properties including system ID.
        """
        pass

    @abstractmethod
    async def create_relationship(self, from_node_id: str, to_node_id: str, rel_type: str, properties: Optional[Dict[str, Any]] = None) -> bool:
        """Create a relationship between two nodes.
        
        Args:
            from_node_id: Source node ID.
            to_node_id: Target node ID.
            rel_type: Relationship type (e.g., "KNOWS").
            properties: Relationship attributes.
            
        Returns:
            True if successful.
        """
        pass

    @abstractmethod
    async def find_shortest_path(self, start_node_id: str, end_node_id: str, max_depth: int = 6) -> List[Dict[str, Any]]:
        """Find the shortest path between two nodes.
        
        Args:
            start_node_id: Starting node ID.
            end_node_id: Ending node ID.
            max_depth: Maximum path length.
            
        Returns:
            List of path elements.
        """
        pass
