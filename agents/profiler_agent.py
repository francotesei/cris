"""Profiler Agent.

Generates behavioral profiles for suspects based on crime scene analysis.
"""

from typing import Any, List, Optional

from core.base_agent import BaseAgent, AgentInput, AgentOutput, AgentCapability
from core.registry import ComponentRegistry
from services.llm_service import LLMService
from config.prompts import PROFILER_PROMPT


@ComponentRegistry.register_agent("profiler_agent")
class ProfilerAgent(BaseAgent):
    """Agent specialized in behavioral profiling and psychological analysis."""
    
    name = "profiler_agent"
    description = "Generates suspect behavioral profiles from crime characteristics."
    
    def __init__(self, llm_service: Optional[LLMService] = None, **kwargs: Any) -> None:
        super().__init__(llm_service=llm_service, **kwargs)
        self.llm_service = llm_service or LLMService()

    async def process(self, input: AgentInput) -> AgentOutput:
        """Analyze case details and generate a profile."""
        self.logger.info(f"Generating profile for case: {input.case_id}")
        
        # In a real app, fetch these from database/context
        case_details = input.context.get("case_details", "Unknown case details")
        crime_scene = input.context.get("crime_scene", "Unknown scene details")
        victim_info = input.context.get("victim_info", "Unknown victim info")
        evidence_summary = input.context.get("evidence_summary", "No evidence summarized")
        
        prompt = PROFILER_PROMPT.format(
            case_details=case_details,
            crime_scene=crime_scene,
            victim_info=victim_info,
            evidence_summary=evidence_summary
        )
        
        try:
            profile_data = await self.llm_service.generate(prompt)
            # Should use generate_structured in production
            
            return AgentOutput(
                agent_name=self.name,
                success=True,
                data={"profile": profile_data},
                confidence=0.8
            )
        except Exception as e:
            self.logger.error(f"Profiling failed: {str(e)}")
            return AgentOutput(agent_name=self.name, success=False, data={}, message=str(e))

    def get_capabilities(self) -> List[AgentCapability]:
        return [
            AgentCapability(
                name="behavioral_profiling",
                description="Generate psychological and behavioral profiles",
                input_types=["case_data"],
                output_types=["suspect_profile"]
            )
        ]
