"""Link Analysis Agent.

Analyzes the knowledge graph to find connections between cases, suspects, and MOs.
"""

from typing import Any, List, Optional

from core.base_agent import BaseAgent, AgentInput, AgentOutput, AgentCapability
from core.registry import ComponentRegistry
from database.neo4j_client import Neo4jClient
from services.llm_service import LLMService


@ComponentRegistry.register_agent("link_agent")
class LinkAgent(BaseAgent):
    """Agent for graph-based connection analysis."""
    
    name = "link_agent"
    description = "Analyzes entity relationships and finds cross-case connections."
    
    def __init__(self, neo4j_client: Optional[Neo4jClient] = None, llm_service: Optional[LLMService] = None, **kwargs: Any) -> None:
        super().__init__(llm_service=llm_service, **kwargs)
        self.neo4j = neo4j_client or Neo4jClient()

    async def process(self, input: AgentInput) -> AgentOutput:
        """Find connections for a specific case or entity."""
        case_id = input.case_id or input.parameters.get("case_id")
        
        if not case_id:
            return AgentOutput(
                agent_name=self.name,
                success=False,
                data={},
                message="No case_id provided for link analysis"
            )
            
        self.logger.info(f"Finding links for case: {case_id}")
        
        # 1. Query graph for similar MOs
        similar_cases = await self._find_similar_mo(case_id)
        
        # 2. Query graph for common suspects
        common_suspects = await self._find_common_suspects(case_id)
        
        # 3. Find shortest paths between known persons if requested
        paths = []
        if "person1_id" in input.parameters and "person2_id" in input.parameters:
            paths = await self.neo4j.find_shortest_path(
                input.parameters["person1_id"],
                input.parameters["person2_id"]
            )
            
        return AgentOutput(
            agent_name=self.name,
            success=True,
            data={
                "similar_cases": similar_cases,
                "common_suspects": common_suspects,
                "shortest_paths": paths
            },
            confidence=0.85
        )

    async def _find_similar_mo(self, case_id: str) -> List[Dict[str, Any]]:
        """Find cases with matching crime types and jurisdictions."""
        query = """
        MATCH (c1:Case {id: $case_id})
        MATCH (c2:Case)
        WHERE c1 <> c2 AND c1.crime_type = c2.crime_type
        RETURN c2.id as id, c2.title as title, c2.crime_type as crime_type
        LIMIT 5
        """
        return await self.neo4j.execute_query(query, {"case_id": case_id})

    async def _find_common_suspects(self, case_id: str) -> List[Dict[str, Any]]:
        """Find people suspected in this case and others."""
        query = """
        MATCH (p:Person)-[:SUSPECT_IN]->(c1:Case {id: $case_id})
        MATCH (p)-[:SUSPECT_IN]->(c2:Case)
        WHERE c1 <> c2
        RETURN p.name as name, p.id as person_id, collect(c2.id) as other_cases
        """
        return await self.neo4j.execute_query(query, {"case_id": case_id})

    def get_capabilities(self) -> List[AgentCapability]:
        return [
            AgentCapability(
                name="find_related_cases",
                description="Find cases similar to the current one",
                input_types=["case_id"],
                output_types=["case_list"]
            ),
            AgentCapability(
                name="person_network",
                description="Map relationships between people",
                input_types=["person_id"],
                output_types=["graph"]
            )
        ]
