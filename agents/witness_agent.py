"""Witness Analysis Agent.

Analyzes witness statements for credibility, inconsistencies, and deception indicators.
"""

from typing import Any, List, Optional

from core.base_agent import BaseAgent, AgentInput, AgentOutput, AgentCapability
from core.registry import ComponentRegistry
from services.llm_service import LLMService
from config.prompts import WITNESS_ANALYSIS_PROMPT


@ComponentRegistry.register_agent("witness_agent")
class WitnessAgent(BaseAgent):
    """Agent specialized in statement analysis and credibility assessment."""
    
    name = "witness_agent"
    description = "Analyzes witness statements for consistency and deception indicators."
    
    def __init__(self, llm_service: Optional[LLMService] = None, **kwargs: Any) -> None:
        super().__init__(llm_service=llm_service, **kwargs)
        self.llm_service = llm_service or LLMService()

    async def process(self, input: AgentInput) -> AgentOutput:
        """Analyze a witness statement."""
        witness_name = input.parameters.get("witness_name", "Unknown")
        self.logger.info(f"Analyzing statement for witness: {witness_name}")
        
        statement_text = input.parameters.get("statement_text", "")
        if not statement_text:
            return AgentOutput(agent_name=self.name, success=False, data={}, message="No statement text provided")
            
        prompt = WITNESS_ANALYSIS_PROMPT.format(
            witness_name=witness_name,
            relationship=input.parameters.get("relationship", "Unknown"),
            statement_date=input.parameters.get("statement_date", "N/A"),
            statement_text=statement_text,
            previous_statements=input.parameters.get("previous_statements", "None"),
            other_statements=input.parameters.get("other_statements", "None")
        )
        
        try:
            analysis = await self.llm_service.generate(prompt)
            return AgentOutput(
                agent_name=self.name,
                success=True,
                data={"analysis": analysis},
                confidence=0.9
            )
        except Exception as e:
            self.logger.error(f"Witness analysis failed: {str(e)}")
            return AgentOutput(agent_name=self.name, success=False, data={}, message=str(e))

    def get_capabilities(self) -> List[AgentCapability]:
        return [
            AgentCapability(
                name="statement_analysis",
                description="Analyze witness statements for credibility",
                input_types=["statement_text"],
                output_types=["credibility_report"]
            )
        ]
