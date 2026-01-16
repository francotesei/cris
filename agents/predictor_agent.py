"""Predictor Agent.

Runs simulations and generates forecasts for future criminal behavior.
"""

from typing import Any, List, Optional

from core.base_agent import BaseAgent, AgentInput, AgentOutput, AgentCapability
from core.registry import ComponentRegistry
from services.llm_service import LLMService
from config.prompts import PREDICTION_PROMPT


@ComponentRegistry.register_agent("predictor_agent")
class PredictorAgent(BaseAgent):
    """Agent specialized in simulation and forecasting."""
    
    name = "predictor_agent"
    description = "Generates forecasts and risk simulations for criminal behavior."
    
    def __init__(self, llm_service: Optional[LLMService] = None, **kwargs: Any) -> None:
        super().__init__(llm_service=llm_service, **kwargs)
        self.llm_service = llm_service or LLMService()

    async def process(self, input: AgentInput) -> AgentOutput:
        """Generate a behavioral forecast."""
        self.logger.info(f"Running predictions for case: {input.case_id}")
        
        # Real app would pull context from other agents/graph
        context = {
            "profile": input.context.get("profile", "Unknown"),
            "history": input.context.get("history", "None"),
            "geo_context": input.context.get("geo_context", "None")
        }
        
        prompt = PREDICTION_PROMPT.format(**context)
        
        try:
            prediction_data = await self.llm_service.generate(prompt)
            
            return AgentOutput(
                agent_name=self.name,
                success=True,
                data={"predictions": prediction_data},
                confidence=0.7
            )
        except Exception as e:
            self.logger.error(f"Prediction failed: {str(e)}")
            return AgentOutput(agent_name=self.name, success=False, data={}, message=str(e))

    def get_capabilities(self) -> List[AgentCapability]:
        return [
            AgentCapability(
                name="escalation_forecasting",
                description="Predict if a suspect will commit more serious crimes",
                input_types=["crime_history"],
                output_types=["risk_score"]
            ),
            AgentCapability(
                name="behavioral_simulation",
                description="Run Monte Carlo simulations of suspect behavior",
                input_types=["profile"],
                output_types=["probability_distribution"]
            )
        ]
