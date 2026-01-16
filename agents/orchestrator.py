"""CRIS Orchestrator Agent - Powered by Gemini 3 + ADK + A2A.

The central coordinator for all CRIS agents. Uses Google's Agent Development Kit (ADK)
for intelligent task routing and the A2A protocol for inter-agent communication.

This agent:
- Receives user queries and determines the best agents to handle them
- Delegates tasks to specialized agents via A2A protocol
- Synthesizes results from multiple agents into coherent reports
- Maintains conversation context across interactions
"""

import asyncio
from typing import Any, AsyncIterator, Callable, Dict, List, Optional

from google import genai
from google.genai import types as genai_types

from core.adk_agent import (
    CRISADKAgent,
    CRISOrchestratorAgent,
    AgentRole,
    AgentCard,
    CRISToolResult,
)
from core.a2a_server import (
    A2AHandler,
    A2AAgentCard,
    A2ASkill,
    A2ARegistry,
    Task,
    Message,
    TaskState,
    ContentPart,
    MessageRole,
)
from core.registry import ComponentRegistry
from config.settings import get_settings
from config.prompts import ORCHESTRATOR_SYSTEM_PROMPT, SYNTHESIS_PROMPT
from utils.logger import get_logger


# System instruction for the orchestrator
ORCHESTRATOR_INSTRUCTION = """You are the CRIS Orchestrator, the central intelligence coordinator for the Criminal Reasoning Intelligence System.

Your responsibilities:
1. ANALYZE user queries to understand their investigative intent
2. DETERMINE which specialized agents should handle the query
3. DELEGATE tasks to appropriate agents using the available tools
4. SYNTHESIZE results from multiple agents into actionable intelligence
5. MAINTAIN context across the investigation

Available Specialized Agents:
- link_agent: Graph analysis, finding connections between cases, suspects, and evidence
- profiler_agent: Behavioral profiling, psychological analysis of suspects
- geo_intel_agent: Geospatial analysis, crime hotspots, movement patterns
- witness_agent: Statement analysis, credibility assessment, inconsistency detection
- predictor_agent: Forecasting, risk assessment, behavioral predictions
- osint_agent: Open-source intelligence, digital footprint analysis

When responding:
- Always explain your reasoning for agent selection
- Provide confidence levels for your assessments
- Highlight critical findings and recommended actions
- Flag any ethical concerns or limitations
- Structure reports for investigator readability

Use the delegate_to_agent tool to send tasks to specialized agents.
Use the synthesize_results tool to combine multiple agent outputs."""


@ComponentRegistry.register_agent("orchestrator")
class OrchestratorAgent(CRISOrchestratorAgent):
    """Main coordinator for the CRIS multi-agent system.
    
    Built on Google ADK with A2A protocol support for seamless
    inter-agent communication and task delegation.
    """
    
    name = "orchestrator"
    description = "Central coordinator that routes queries to specialized agents and synthesizes results."
    model = "gemini-2.0-flash"  # Gemini 3
    role = AgentRole.ORCHESTRATOR
    
    def __init__(self, **kwargs: Any) -> None:
        """Initialize the orchestrator with ADK and A2A support."""
        super().__init__(
            system_instruction=ORCHESTRATOR_INSTRUCTION,
            **kwargs
        )
        self.settings = get_settings()
        self.a2a_registry = A2ARegistry()
        self._pending_results: Dict[str, List[Dict[str, Any]]] = {}
        
        # Register this agent with A2A
        self._setup_a2a_handler()
    
    def _setup_a2a_handler(self) -> None:
        """Configure the A2A handler for this agent."""
        agent_card = A2AAgentCard(
            name=self.name,
            description=self.description,
            version="2.0.0",
            capabilities={
                "streaming": True,
                "pushNotifications": False,
                "stateTransitionHistory": True,
            },
            skills=[
                A2ASkill(
                    id="case_analysis",
                    name="Full Case Analysis",
                    description="Comprehensive analysis of a criminal case using all available agents",
                    tags=["investigation", "analysis", "multi-agent"],
                    examples=[
                        "Analyze case CASE-2024-001",
                        "What connections exist between suspect John Doe and the robbery cases?",
                    ]
                ),
                A2ASkill(
                    id="query_routing",
                    name="Intelligent Query Routing",
                    description="Route investigative queries to the most appropriate specialized agents",
                    tags=["routing", "delegation"],
                    examples=[
                        "Find similar cases to this homicide",
                        "Generate a behavioral profile for the suspect",
                    ]
                ),
                A2ASkill(
                    id="synthesis",
                    name="Multi-Agent Synthesis",
                    description="Combine results from multiple agents into actionable intelligence",
                    tags=["synthesis", "reporting"],
                )
            ]
        )
        
        handler = A2AHandler(
            agent_card=agent_card,
            task_handler=self._handle_a2a_task
        )
        self.a2a_registry.register(handler)
    
    async def _handle_a2a_task(
        self,
        task: Task,
        message: Message
    ) -> AsyncIterator[Dict[str, Any]]:
        """Handle incoming A2A tasks.
        
        Args:
            task: The A2A task.
            message: The incoming message.
            
        Yields:
            Task events (status updates, artifacts).
        """
        # Extract query from message
        query = ""
        for part in message.parts:
            if part.text:
                query += part.text
        
        # Process through ADK agent
        result = await self.run(
            query=query,
            session_id=task.session_id,
            context=task.metadata
        )
        
        # Yield result as artifact
        yield {
            "type": "artifact",
            "artifact": {
                "name": "analysis_report",
                "description": "Orchestrator analysis and synthesis",
                "parts": [{"type": "text", "text": result["response"]}],
                "index": 0,
                "last_chunk": True
            }
        }
    
    def get_tools(self) -> List[Callable]:
        """Return orchestrator-specific tools."""
        return [
            self.delegate_to_agent,
            self.synthesize_results,
            self.get_available_agents,
            self.analyze_case,
        ]
    
    async def delegate_to_agent(
        self,
        agent_name: str,
        query: str,
        context: Optional[Dict[str, Any]] = None
    ) -> CRISToolResult:
        """Delegate a task to a specialized agent.
        
        Use this tool to send specific tasks to agents like link_agent,
        profiler_agent, geo_intel_agent, witness_agent, predictor_agent, or osint_agent.
        
        Args:
            agent_name: Name of the target agent (e.g., "link_agent", "profiler_agent")
            query: The specific task or question for the agent
            context: Additional context like case_id, parameters, etc.
            
        Returns:
            Result from the delegated agent including success status and data.
        """
        self.logger.info(f"Delegating to {agent_name}: {query[:100]}...")
        
        # Check if agent is registered locally
        if agent_name in self._sub_agents:
            result = await self._sub_agents[agent_name].run(query, context=context)
            return CRISToolResult(
                success=True,
                data=result,
                confidence=0.9
            )
        
        # Try A2A registry for local agents
        try:
            task = await self.a2a_registry.route_task(agent_name, query)
            
            # Extract response from task artifacts
            response_text = ""
            for artifact in task.artifacts:
                for part in artifact.parts:
                    if part.text:
                        response_text += part.text
            
            return CRISToolResult(
                success=task.status.state == TaskState.COMPLETED,
                data={"response": response_text, "artifacts": [a.model_dump() for a in task.artifacts]},
                message=f"Task completed via A2A: {task.id}",
                confidence=0.85
            )
        except ValueError as e:
            return CRISToolResult(
                success=False,
                data={},
                message=f"Agent not found: {agent_name}. Available: {list(self._sub_agents.keys())}",
                confidence=0.0
            )
    
    async def synthesize_results(
        self,
        results: List[Dict[str, Any]],
        original_query: str
    ) -> CRISToolResult:
        """Synthesize results from multiple agents into a coherent report.
        
        Use this after collecting results from multiple agents to create
        a unified analysis report.
        
        Args:
            results: List of results from different agents
            original_query: The original user query for context
            
        Returns:
            Synthesized report combining all agent insights.
        """
        self.logger.info(f"Synthesizing {len(results)} agent results")
        
        # Build synthesis prompt
        results_text = "\n\n---\n\n".join([
            f"**Agent: {r.get('agent', 'Unknown')}**\n{r.get('response', str(r.get('data', 'No data')))}"
            for r in results
        ])
        
        synthesis_prompt = f"""Based on the following results from specialized agents, create a comprehensive
investigative report that answers the original query.

ORIGINAL QUERY: {original_query}

AGENT RESULTS:
{results_text}

Create a synthesis that:
1. Highlights key findings from each agent
2. Identifies connections and patterns across results
3. Resolves any contradictions or conflicts
4. Provides actionable recommendations
5. Notes confidence levels and limitations

Format as a professional investigative report."""

        # Use Gemini to synthesize
        response = self._client.models.generate_content(
            model=self._model,
            contents=synthesis_prompt
        )
        
        return CRISToolResult(
            success=True,
            data={"report": response.text, "sources": len(results)},
            confidence=0.9
        )
    
    async def get_available_agents(self) -> CRISToolResult:
        """Get information about all available specialized agents.
        
        Returns a list of agents with their capabilities and descriptions.
        Useful for understanding what analysis options are available.
        
        Returns:
            List of available agents and their capabilities.
        """
        # Combine local sub-agents and A2A registry
        agents_info = []
        
        # Local sub-agents
        for name, agent in self._sub_agents.items():
            card = agent.get_agent_card()
            agents_info.append({
                "name": name,
                "description": card.description,
                "capabilities": card.capabilities,
                "type": "local"
            })
        
        # A2A registered agents
        for card in self.a2a_registry.list_agents():
            if card.name not in [a["name"] for a in agents_info]:
                agents_info.append({
                    "name": card.name,
                    "description": card.description,
                    "skills": [s.model_dump() for s in card.skills],
                    "type": "a2a"
                })
        
        return CRISToolResult(
            success=True,
            data={"agents": agents_info, "count": len(agents_info)},
            confidence=1.0
        )
    
    async def analyze_case(
        self,
        case_id: str,
        analysis_types: Optional[List[str]] = None
    ) -> CRISToolResult:
        """Perform a comprehensive analysis of a case using multiple agents.
        
        This is a high-level tool that automatically delegates to relevant
        agents based on the case and requested analysis types.
        
        Args:
            case_id: The case identifier to analyze
            analysis_types: Optional list of specific analyses to run.
                           Options: "links", "profile", "geo", "witness", "predict", "osint"
                           If not specified, runs all relevant analyses.
                           
        Returns:
            Comprehensive case analysis from multiple agents.
        """
        self.logger.info(f"Starting comprehensive analysis for case: {case_id}")
        
        # Default to all analysis types
        if not analysis_types:
            analysis_types = ["links", "profile", "geo", "predict"]
        
        # Map analysis types to agents
        agent_map = {
            "links": ("link_agent", f"Find all connections and similar cases for case {case_id}"),
            "profile": ("profiler_agent", f"Generate behavioral profile for suspects in case {case_id}"),
            "geo": ("geo_intel_agent", f"Analyze geographic patterns for case {case_id}"),
            "witness": ("witness_agent", f"Analyze witness statements for case {case_id}"),
            "predict": ("predictor_agent", f"Generate risk predictions for case {case_id}"),
            "osint": ("osint_agent", f"Gather open-source intelligence for case {case_id}"),
        }
        
        # Execute relevant agents in parallel
        tasks = []
        for analysis_type in analysis_types:
            if analysis_type in agent_map:
                agent_name, query = agent_map[analysis_type]
                tasks.append(self.delegate_to_agent(agent_name, query, {"case_id": case_id}))
        
        if not tasks:
            return CRISToolResult(
                success=False,
                data={},
                message="No valid analysis types specified"
            )
        
        # Gather results
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Filter successful results
        successful_results = []
        for i, result in enumerate(results):
            if isinstance(result, CRISToolResult) and result.success:
                successful_results.append({
                    "agent": analysis_types[i],
                    "data": result.data
                })
        
        # Synthesize if we have multiple results
        if len(successful_results) > 1:
            synthesis = await self.synthesize_results(
                successful_results,
                f"Comprehensive analysis of case {case_id}"
            )
            return CRISToolResult(
                success=True,
                data={
                    "case_id": case_id,
                    "individual_results": successful_results,
                    "synthesis": synthesis.data
                },
                confidence=0.85
            )
        
        return CRISToolResult(
            success=len(successful_results) > 0,
            data={
                "case_id": case_id,
                "results": successful_results
            },
            confidence=0.8 if successful_results else 0.0
        )
    
    async def process_query(
        self,
        query: str,
        case_id: Optional[str] = None,
        session_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """Process a natural language query through the orchestrator.
        
        This is the main entry point for user queries. The orchestrator
        will analyze the query, determine which agents to involve, and
        synthesize a comprehensive response.
        
        Args:
            query: The user's natural language query.
            case_id: Optional case context.
            session_id: Optional session for conversation continuity.
            
        Returns:
            Comprehensive response with analysis and recommendations.
        """
        context = {}
        if case_id:
            context["case_id"] = case_id
        
        # Run through ADK agent
        result = await self.run(
            query=query,
            session_id=session_id,
            context=context
        )
        
        return result


# Factory function for easy instantiation
def create_orchestrator(
    sub_agents: Optional[List[CRISADKAgent]] = None,
    **kwargs: Any
) -> OrchestratorAgent:
    """Create and configure an orchestrator agent.
    
    Args:
        sub_agents: Optional list of agents to register.
        **kwargs: Additional configuration.
        
    Returns:
        Configured OrchestratorAgent.
    """
    orchestrator = OrchestratorAgent(**kwargs)
    
    if sub_agents:
        for agent in sub_agents:
            orchestrator.register_agent(agent)
    
    return orchestrator
