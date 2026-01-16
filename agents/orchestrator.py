"""Orchestrator Agent.

The central coordinator for all CRIS agents. Handles query routing and synthesis.
"""

import asyncio
from typing import Any, Dict, List, Optional

from core.base_agent import BaseAgent, AgentInput, AgentOutput, AgentCapability
from core.registry import ComponentRegistry
from services.llm_service import LLMService
from config.prompts import INTENT_PARSING_PROMPT, SYNTHESIS_PROMPT


@ComponentRegistry.register_agent("orchestrator")
class OrchestratorAgent(BaseAgent):
    """Main coordinator for CRIS multi-agent system."""
    
    name = "orchestrator"
    description = "Coordinates all agents and synthesizes results."
    
    def __init__(self, llm_service: Optional[LLMService] = None, **kwargs: Any) -> None:
        super().__init__(llm_service=llm_service, **kwargs)
        self.llm_service = llm_service or LLMService()
        self.agents: Dict[str, BaseAgent] = {}

    def register_subagent(self, agent: BaseAgent) -> None:
        """Connect a sub-agent to the orchestrator."""
        self.agents[agent.name] = agent
        self.logger.info(f"Registered sub-agent: {agent.name}")

    async def process(self, input: AgentInput) -> AgentOutput:
        """The main entry point for user queries.
        
        Flow:
        1. Parse intent and determine required agents.
        2. Activate agents in parallel.
        3. Synthesize results into a final report.
        """
        self.logger.info(f"Processing orchestrator query: {input.query}")
        
        # 1. Parse intent
        intent = await self._parse_intent(input.query, input.case_id)
        target_agent_names = intent.get("required_agents", [])
        
        # 2. Execute agents in parallel
        tasks = []
        for name in target_agent_names:
            if name in self.agents:
                sub_input = AgentInput(
                    query=input.query,
                    case_id=input.case_id,
                    parameters=intent.get("parameters", {})
                )
                tasks.append(self.agents[name].process(sub_input))
                
        if not tasks:
            # Fallback to direct LLM answer if no specialized agents needed
            answer = await self.llm_service.generate(input.query)
            return AgentOutput(
                agent_name=self.name,
                success=True,
                data={"report": answer},
                message="Direct LLM response"
            )
            
        agent_results = await asyncio.gather(*tasks)
        
        # 3. Synthesize results
        report = await self._synthesize_results(input.query, agent_results)
        
        return AgentOutput(
            agent_name=self.name,
            success=True,
            data={
                "report": report,
                "agent_outputs": [res.model_dump() for res in agent_results]
            }
        )

    async def _parse_intent(self, query: str, case_id: Optional[str]) -> Dict[str, Any]:
        """Use LLM to determine which agents to call."""
        # Simple implementation for now - in production use structured generation
        prompt = INTENT_PARSING_PROMPT.format(query=query, case_context=f"Case ID: {case_id}")
        # Note: Ideally use generate_structured here
        response = await self.llm_service.generate(prompt)
        # Mocking parsing for this example
        return {"required_agents": ["link_agent"], "parameters": {}}

    async def _synthesize_results(self, query: str, results: List[AgentOutput]) -> str:
        """Combine multiple agent outputs into a markdown report."""
        results_str = "\n---\n".join([f"AGENT: {res.agent_name}\nDATA: {str(res.data)}" for res in results])
        prompt = SYNTHESIS_PROMPT.format(query=query, agent_results=results_str)
        return await self.llm_service.generate(prompt)

    def get_capabilities(self) -> List[AgentCapability]:
        return [
            AgentCapability(
                name="orchestration",
                description="Routes queries to specialized agents",
                input_types=["text"],
                output_types=["investigative_report"]
            )
        ]
