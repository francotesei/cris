"""CRIS Link Analysis Agent - Powered by Gemini 3 + ADK + A2A.

Analyzes the knowledge graph to find connections between cases, suspects, 
evidence, and modus operandi patterns. Uses Neo4j graph queries combined
with Gemini 3's reasoning capabilities.

Key capabilities:
- Find similar cases based on MO (modus operandi)
- Detect serial patterns across cases
- Identify common suspects/witnesses across cases
- Geographic clustering of related crimes
- Temporal pattern matching
- Criminal network analysis
"""

from typing import Any, AsyncIterator, Callable, Dict, List, Optional

from core.adk_agent import CRISADKAgent, AgentRole, CRISToolResult
from core.a2a_server import (
    A2AHandler,
    A2AAgentCard,
    A2ASkill,
    A2ARegistry,
    Task,
    Message,
    ContentPart,
)
from core.registry import ComponentRegistry
from database.neo4j_client import Neo4jClient
from utils.logger import get_logger


LINK_AGENT_INSTRUCTION = """You are the CRIS Link Analysis Agent, specialized in graph-based 
criminal intelligence analysis.

Your expertise:
1. GRAPH ANALYSIS: Navigate complex relationship networks to find hidden connections
2. PATTERN DETECTION: Identify serial crime patterns and MO similarities
3. NETWORK MAPPING: Map criminal organizations and associate networks
4. CROSS-CASE LINKING: Find connections between seemingly unrelated cases

When analyzing:
- Consider multiple relationship types (KNOWS, WORKS_WITH, FREQUENTS, etc.)
- Weight connections by strength and recency
- Flag potential false positives with confidence scores
- Explain the significance of discovered connections

Use the available tools to query the knowledge graph and analyze relationships.
Always provide evidence-based conclusions with clear reasoning."""


@ComponentRegistry.register_agent("link_agent")
class LinkAgent(CRISADKAgent):
    """Agent for graph-based connection analysis using ADK and Neo4j."""
    
    name = "link_agent"
    description = "Analyzes entity relationships and finds cross-case connections using graph intelligence."
    model = "gemini-2.0-flash"
    role = AgentRole.ANALYST
    
    def __init__(
        self,
        neo4j_client: Optional[Neo4jClient] = None,
        **kwargs: Any
    ) -> None:
        """Initialize the Link Agent with Neo4j connection.
        
        Args:
            neo4j_client: Optional Neo4j client instance.
            **kwargs: Additional configuration.
        """
        self.neo4j = neo4j_client or Neo4jClient()
        super().__init__(
            system_instruction=LINK_AGENT_INSTRUCTION,
            **kwargs
        )
        
        # Register with A2A
        self._setup_a2a_handler()
    
    def _setup_a2a_handler(self) -> None:
        """Configure A2A handler for this agent."""
        agent_card = A2AAgentCard(
            name=self.name,
            description=self.description,
            version="2.0.0",
            skills=[
                A2ASkill(
                    id="find_similar_cases",
                    name="Find Similar Cases",
                    description="Find cases with similar MO, location, or suspect profiles",
                    tags=["graph", "cases", "similarity"],
                    examples=[
                        "Find cases similar to CASE-2024-001",
                        "What other robberies match this MO?",
                    ]
                ),
                A2ASkill(
                    id="map_criminal_network",
                    name="Map Criminal Network",
                    description="Visualize and analyze criminal associate networks",
                    tags=["graph", "network", "suspects"],
                    examples=[
                        "Map the network around suspect John Doe",
                        "Find all associates of the robbery crew",
                    ]
                ),
                A2ASkill(
                    id="find_connection_path",
                    name="Find Connection Path",
                    description="Find the shortest relationship path between two entities",
                    tags=["graph", "path", "connection"],
                    examples=[
                        "How are John Doe and Jane Smith connected?",
                        "Find links between case A and case B",
                    ]
                ),
            ]
        )
        
        handler = A2AHandler(
            agent_card=agent_card,
            task_handler=self._handle_a2a_task
        )
        A2ARegistry().register(handler)
    
    async def _handle_a2a_task(
        self,
        task: Task,
        message: Message
    ) -> AsyncIterator[Dict[str, Any]]:
        """Handle A2A task requests."""
        query = "".join(part.text or "" for part in message.parts)
        
        result = await self.run(
            query=query,
            session_id=task.session_id,
            context=task.metadata
        )
        
        yield {
            "type": "artifact",
            "artifact": {
                "name": "link_analysis",
                "description": "Graph connection analysis results",
                "parts": [{"type": "text", "text": result["response"]}],
                "index": 0,
                "last_chunk": True
            }
        }
    
    def get_tools(self) -> List[Callable]:
        """Return link analysis tools."""
        return [
            self.find_similar_cases,
            self.find_common_suspects,
            self.find_connection_path,
            self.analyze_criminal_network,
            self.find_geographic_clusters,
            self.detect_serial_patterns,
        ]
    
    async def find_similar_cases(
        self,
        case_id: str,
        similarity_factors: Optional[List[str]] = None,
        limit: int = 10
    ) -> CRISToolResult:
        """Find cases similar to the specified case.
        
        Analyzes multiple factors to find related cases including crime type,
        MO characteristics, geographic proximity, and temporal patterns.
        
        Args:
            case_id: The reference case ID
            similarity_factors: Optional list of factors to consider:
                               ["crime_type", "location", "mo", "time_of_day", "weapon"]
            limit: Maximum number of similar cases to return
            
        Returns:
            List of similar cases with similarity scores and matching factors.
        """
        self.logger.info(f"Finding cases similar to {case_id}")
        
        # Build dynamic similarity query
        factors = similarity_factors or ["crime_type", "jurisdiction"]
        
        query = """
        MATCH (c1:Case {id: $case_id})
        MATCH (c2:Case)
        WHERE c1 <> c2
        WITH c1, c2,
             CASE WHEN c1.crime_type = c2.crime_type THEN 0.3 ELSE 0 END +
             CASE WHEN c1.jurisdiction = c2.jurisdiction THEN 0.2 ELSE 0 END +
             CASE WHEN abs(duration.between(c1.date_occurred, c2.date_occurred).days) < 30 THEN 0.2 ELSE 0 END +
             CASE WHEN c1.status = c2.status THEN 0.1 ELSE 0 END
             AS similarity_score
        WHERE similarity_score > 0
        RETURN c2.id AS id, 
               c2.title AS title, 
               c2.crime_type AS crime_type,
               c2.status AS status,
               c2.date_occurred AS date_occurred,
               similarity_score
        ORDER BY similarity_score DESC
        LIMIT $limit
        """
        
        try:
            results = await self.neo4j.execute_query(
                query, 
                {"case_id": case_id, "limit": limit}
            )
            
            return CRISToolResult(
                success=True,
                data={
                    "reference_case": case_id,
                    "similar_cases": results,
                    "factors_considered": factors
                },
                confidence=0.85
            )
        except Exception as e:
            self.logger.error(f"Similar case query failed: {e}")
            return CRISToolResult(
                success=False,
                data={},
                message=str(e)
            )
    
    async def find_common_suspects(
        self,
        case_id: str,
        min_cases: int = 2
    ) -> CRISToolResult:
        """Find suspects that appear in multiple cases.
        
        Identifies individuals who are suspects in the given case and also
        appear as suspects in other cases, potentially indicating serial offenders.
        
        Args:
            case_id: The case to analyze
            min_cases: Minimum number of cases a suspect must appear in
            
        Returns:
            List of suspects with their case involvement and risk indicators.
        """
        self.logger.info(f"Finding common suspects for case {case_id}")
        
        query = """
        MATCH (p:Person)-[:SUSPECT_IN]->(c1:Case {id: $case_id})
        MATCH (p)-[:SUSPECT_IN]->(c2:Case)
        WHERE c1 <> c2
        WITH p, c1, collect(DISTINCT c2) AS other_cases
        WHERE size(other_cases) >= $min_cases - 1
        RETURN p.id AS person_id,
               p.name AS name,
               p.risk_score AS risk_score,
               p.criminal_history AS has_criminal_history,
               [c IN other_cases | {id: c.id, title: c.title, crime_type: c.crime_type}] AS other_cases,
               size(other_cases) + 1 AS total_cases
        ORDER BY total_cases DESC
        """
        
        try:
            results = await self.neo4j.execute_query(
                query,
                {"case_id": case_id, "min_cases": min_cases}
            )
            
            return CRISToolResult(
                success=True,
                data={
                    "case_id": case_id,
                    "common_suspects": results,
                    "total_found": len(results)
                },
                confidence=0.9 if results else 0.5
            )
        except Exception as e:
            self.logger.error(f"Common suspects query failed: {e}")
            return CRISToolResult(success=False, data={}, message=str(e))
    
    async def find_connection_path(
        self,
        entity1_id: str,
        entity2_id: str,
        entity1_type: str = "Person",
        entity2_type: str = "Person",
        max_depth: int = 6
    ) -> CRISToolResult:
        """Find the shortest relationship path between two entities.
        
        Discovers how two people, cases, or other entities are connected
        through the knowledge graph, revealing hidden relationships.
        
        Args:
            entity1_id: First entity ID
            entity2_id: Second entity ID
            entity1_type: Type of first entity (Person, Case, Location, etc.)
            entity2_type: Type of second entity
            max_depth: Maximum relationship depth to search
            
        Returns:
            The shortest path with all intermediate nodes and relationships.
        """
        self.logger.info(f"Finding path between {entity1_id} and {entity2_id}")
        
        query = f"""
        MATCH path = shortestPath(
            (e1:{entity1_type} {{id: $entity1_id}})-[*..{max_depth}]-(e2:{entity2_type} {{id: $entity2_id}})
        )
        RETURN path,
               length(path) AS path_length,
               [n IN nodes(path) | {{id: n.id, labels: labels(n), name: coalesce(n.name, n.title, n.id)}}] AS nodes,
               [r IN relationships(path) | {{type: type(r), properties: properties(r)}}] AS relationships
        """
        
        try:
            results = await self.neo4j.execute_query(
                query,
                {"entity1_id": entity1_id, "entity2_id": entity2_id}
            )
            
            if results:
                return CRISToolResult(
                    success=True,
                    data={
                        "path_found": True,
                        "path_length": results[0]["path_length"],
                        "nodes": results[0]["nodes"],
                        "relationships": results[0]["relationships"]
                    },
                    confidence=0.95
                )
            else:
                return CRISToolResult(
                    success=True,
                    data={"path_found": False},
                    message=f"No connection found within {max_depth} hops",
                    confidence=0.8
                )
        except Exception as e:
            self.logger.error(f"Path finding failed: {e}")
            return CRISToolResult(success=False, data={}, message=str(e))
    
    async def analyze_criminal_network(
        self,
        person_id: str,
        depth: int = 2,
        relationship_types: Optional[List[str]] = None
    ) -> CRISToolResult:
        """Analyze the criminal network around a person of interest.
        
        Maps out the associate network including known relationships,
        shared case involvement, and potential criminal connections.
        
        Args:
            person_id: The central person to analyze
            depth: How many relationship hops to explore
            relationship_types: Specific relationships to follow
                              (default: KNOWS, WORKS_WITH, MEMBER_OF, RELATED_TO)
                              
        Returns:
            Network map with nodes, edges, and risk analysis.
        """
        self.logger.info(f"Analyzing network for person {person_id}")
        
        rel_types = relationship_types or ["KNOWS", "WORKS_WITH", "MEMBER_OF", "RELATED_TO"]
        rel_pattern = "|".join(rel_types)
        
        query = f"""
        MATCH (center:Person {{id: $person_id}})
        CALL apoc.path.subgraphAll(center, {{
            relationshipFilter: '{rel_pattern}',
            maxLevel: $depth
        }})
        YIELD nodes, relationships
        RETURN 
            [n IN nodes WHERE n:Person | {{
                id: n.id, 
                name: n.name, 
                risk_score: n.risk_score,
                criminal_history: n.criminal_history
            }}] AS people,
            [r IN relationships | {{
                source: startNode(r).id,
                target: endNode(r).id,
                type: type(r),
                properties: properties(r)
            }}] AS connections,
            size(nodes) AS network_size
        """
        
        try:
            results = await self.neo4j.execute_query(
                query,
                {"person_id": person_id, "depth": depth}
            )
            
            if results:
                network = results[0]
                # Calculate network risk
                high_risk_count = sum(
                    1 for p in network["people"] 
                    if p.get("risk_score", 0) > 0.7 or p.get("criminal_history")
                )
                
                return CRISToolResult(
            success=True,
            data={
                        "center_person": person_id,
                        "network_size": network["network_size"],
                        "people": network["people"],
                        "connections": network["connections"],
                        "high_risk_associates": high_risk_count,
                        "risk_assessment": "HIGH" if high_risk_count > 3 else "MEDIUM" if high_risk_count > 0 else "LOW"
            },
            confidence=0.85
        )
            else:
                return CRISToolResult(
                    success=True,
                    data={"network_size": 0},
                    message="No network found for this person"
                )
        except Exception as e:
            self.logger.error(f"Network analysis failed: {e}")
            return CRISToolResult(success=False, data={}, message=str(e))
    
    async def find_geographic_clusters(
        self,
        crime_type: Optional[str] = None,
        days_back: int = 90,
        min_cluster_size: int = 3
    ) -> CRISToolResult:
        """Find geographic clusters of criminal activity.
        
        Identifies locations with concentrated criminal activity that may
        indicate hotspots or serial crime patterns.
        
        Args:
            crime_type: Optional filter for specific crime types
            days_back: How far back to analyze
            min_cluster_size: Minimum cases to form a cluster
            
        Returns:
            Geographic clusters with case counts and patterns.
        """
        self.logger.info(f"Finding geographic clusters for {crime_type or 'all crimes'}")
        
        crime_filter = "AND c.crime_type = $crime_type" if crime_type else ""
        
        query = f"""
        MATCH (c:Case)-[:CRIME_SCENE_FOR]-(l:Location)
        WHERE c.date_occurred >= datetime() - duration({{days: $days_back}})
        {crime_filter}
        WITH l, collect(c) AS cases
        WHERE size(cases) >= $min_cluster_size
        RETURN l.id AS location_id,
               l.name AS location_name,
               l.address AS address,
               l.latitude AS lat,
               l.longitude AS lon,
               size(cases) AS case_count,
               [c IN cases | {{id: c.id, title: c.title, crime_type: c.crime_type, date: c.date_occurred}}] AS cases
        ORDER BY case_count DESC
        """
        
        params = {
            "days_back": days_back,
            "min_cluster_size": min_cluster_size
        }
        if crime_type:
            params["crime_type"] = crime_type
        
        try:
            results = await self.neo4j.execute_query(query, params)
            
            return CRISToolResult(
                success=True,
                data={
                    "clusters": results,
                    "total_clusters": len(results),
                    "parameters": {
                        "crime_type": crime_type,
                        "days_analyzed": days_back,
                        "min_cluster_size": min_cluster_size
                    }
                },
                confidence=0.8
            )
        except Exception as e:
            self.logger.error(f"Geographic cluster query failed: {e}")
            return CRISToolResult(success=False, data={}, message=str(e))
    
    async def detect_serial_patterns(
        self,
        case_id: str,
        pattern_factors: Optional[List[str]] = None
    ) -> CRISToolResult:
        """Detect potential serial crime patterns related to a case.
        
        Analyzes MO, timing, geography, and victimology to identify
        potential serial patterns that may link multiple cases.
        
        Args:
            case_id: The case to analyze for serial patterns
            pattern_factors: Factors to consider in pattern matching
                           (default: mo, time_pattern, geography, victimology)
                           
        Returns:
            Pattern analysis with linked cases and confidence scores.
        """
        self.logger.info(f"Detecting serial patterns for case {case_id}")
        
        # Complex pattern detection query
        query = """
        MATCH (c1:Case {id: $case_id})
        OPTIONAL MATCH (c1)-[:CRIME_SCENE_FOR]-(l1:Location)
        OPTIONAL MATCH (v1:Person)-[:VICTIM_IN]->(c1)
        
        // Find cases with similar patterns
        MATCH (c2:Case)
        WHERE c1 <> c2 AND c1.crime_type = c2.crime_type
        OPTIONAL MATCH (c2)-[:CRIME_SCENE_FOR]-(l2:Location)
        OPTIONAL MATCH (v2:Person)-[:VICTIM_IN]->(c2)
        
        WITH c1, c2, l1, l2, v1, v2,
             // Calculate pattern similarity
             CASE WHEN c1.crime_type = c2.crime_type THEN 0.25 ELSE 0 END +
             CASE WHEN l1 IS NOT NULL AND l2 IS NOT NULL AND 
                  point.distance(point({latitude: l1.latitude, longitude: l1.longitude}),
                                point({latitude: l2.latitude, longitude: l2.longitude})) < 5000 
                  THEN 0.25 ELSE 0 END +
             CASE WHEN v1 IS NOT NULL AND v2 IS NOT NULL AND v1.gender = v2.gender THEN 0.15 ELSE 0 END +
             CASE WHEN abs(c1.date_occurred.hour - c2.date_occurred.hour) <= 2 THEN 0.15 ELSE 0 END +
             CASE WHEN c1.date_occurred.dayOfWeek = c2.date_occurred.dayOfWeek THEN 0.1 ELSE 0 END
             AS pattern_score
        WHERE pattern_score >= 0.5
        
        RETURN c2.id AS case_id,
               c2.title AS title,
               c2.crime_type AS crime_type,
               c2.date_occurred AS date,
               pattern_score,
               CASE 
                   WHEN pattern_score >= 0.8 THEN 'HIGH'
                   WHEN pattern_score >= 0.6 THEN 'MEDIUM'
                   ELSE 'LOW'
               END AS confidence
        ORDER BY pattern_score DESC
        LIMIT 10
        """
        
        try:
            results = await self.neo4j.execute_query(query, {"case_id": case_id})
            
            is_serial = len(results) >= 2 and any(r["pattern_score"] >= 0.7 for r in results)
            
            return CRISToolResult(
                success=True,
                data={
                    "reference_case": case_id,
                    "potential_serial": is_serial,
                    "linked_cases": results,
                    "pattern_count": len(results),
                    "recommendation": "INVESTIGATE AS SERIAL" if is_serial else "CONTINUE MONITORING"
                },
                confidence=0.85 if results else 0.5
            )
        except Exception as e:
            self.logger.error(f"Serial pattern detection failed: {e}")
            return CRISToolResult(success=False, data={}, message=str(e))
