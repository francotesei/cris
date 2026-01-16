"""Neo4j Database Client.

Implementation of BaseGraphDB using the official Neo4j Python driver.
"""

from typing import Any, Dict, List, Optional
from neo4j import AsyncGraphDatabase, AsyncDriver

from core.base_graph_db import BaseGraphDB
from config.settings import get_settings
from utils.logger import get_logger


class Neo4jClient(BaseGraphDB):
    """Async client for Neo4j graph database."""
    
    def __init__(self, uri: str = None, user: str = None, password: str = None) -> None:
        """Initialize the client.
        
        Args:
            uri: Neo4j Bolt/Neo4j URI.
            user: Username.
            password: Password.
        """
        settings = get_settings()
        self.uri = uri or settings.neo4j_uri
        self.user = user or settings.neo4j_user
        self.password = password or settings.neo4j_password
        self.driver: Optional[AsyncDriver] = None
        self.logger = get_logger("database.neo4j")

    async def connect(self) -> None:
        """Establish connection to Neo4j."""
        if not self.driver:
            self.driver = AsyncGraphDatabase.driver(
                self.uri, 
                auth=(self.user, self.password)
            )
            self.logger.info(f"Connected to Neo4j at {self.uri}")

    async def close(self) -> None:
        """Close the connection."""
        if self.driver:
            await self.driver.close()
            self.driver = None

    async def execute_query(self, query: str, parameters: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """Execute a Cypher query."""
        if not self.driver:
            await self.connect()
            
        async with self.driver.session() as session:
            result = await session.run(query, parameters or {})
            records = await result.data()
            return records

    async def create_node(self, label: str, properties: Dict[str, Any]) -> Dict[str, Any]:
        """Create a node with a label and properties."""
        query = f"CREATE (n:{label} $props) RETURN n"
        result = await self.execute_query(query, {"props": properties})
        return result[0]["n"] if result else {}

    async def create_relationship(self, from_node_id: str, to_node_id: str, rel_type: str, properties: Optional[Dict[str, Any]] = None) -> bool:
        """Create a relationship between two nodes by their system IDs."""
        query = f"""
        MATCH (a), (b)
        WHERE elementId(a) = $from_id AND elementId(b) = $to_id
        CREATE (a)-[r:{rel_type} $props]->(b)
        RETURN r
        """
        params = {
            "from_id": from_node_id,
            "to_id": to_node_id,
            "props": properties or {}
        }
        result = await self.execute_query(query, params)
        return len(result) > 0

    async def find_shortest_path(self, start_node_id: str, end_node_id: str, max_depth: int = 6) -> List[Dict[str, Any]]:
        """Find the shortest path using Neo4j's shortestPath function."""
        query = f"""
        MATCH (start), (end)
        WHERE elementId(start) = $start_id AND elementId(end) = $end_id
        MATCH p = shortestPath((start)-[*..{max_depth}]-(end))
        RETURN p
        """
        params = {"start_id": start_node_id, "end_id": end_node_id}
        result = await self.execute_query(query, params)
        return result
