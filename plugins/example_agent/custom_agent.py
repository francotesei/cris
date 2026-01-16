"""Example Custom Agent.

This module demonstrates how to create a custom agent plugin for CRIS.
Use this as a template for your own agents.
"""

from typing import Any

from core.base_agent import BaseAgent, AgentInput, AgentOutput, AgentCapability
from core.registry import ComponentRegistry


@ComponentRegistry.register_agent("example")
class ExampleAgent(BaseAgent):
    """Example agent demonstrating plugin architecture.
    
    This agent serves as a template for creating custom agents.
    Replace this implementation with your own logic.
    
    Attributes:
        name: Unique identifier for this agent
        description: Human-readable description of the agent's purpose
    """
    
    name = "example"
    description = "Example agent for demonstration purposes"
    version = "1.0.0"
    
    def __init__(self, llm_service: Any = None, **kwargs: Any) -> None:
        """Initialize the example agent.
        
        Args:
            llm_service: Optional LLM service for AI capabilities
            **kwargs: Additional configuration options
        """
        super().__init__(llm_service=llm_service, **kwargs)
    
    async def process(self, input: AgentInput) -> AgentOutput:
        """Process input and return analysis results.
        
        This is the main entry point for the agent. Implement your
        custom logic here.
        
        Args:
            input: The input data to process
            
        Returns:
            AgentOutput containing the analysis results
        """
        self.logger.info(f"Processing input for case: {input.case_id}")
        
        # Example processing logic
        result = {
            "status": "success",
            "message": "Example agent processed successfully",
            "input_summary": {
                "case_id": input.case_id,
                "query": input.query,
            },
        }
        
        return AgentOutput(
            agent_name=self.name,
            success=True,
            data=result,
            confidence=1.0,
            metadata={"version": self.version},
        )
    
    def get_capabilities(self) -> list[AgentCapability]:
        """Return the list of capabilities this agent provides.
        
        Returns:
            List of AgentCapability objects describing what this agent can do
        """
        return [
            AgentCapability(
                name="example_analysis",
                description="Demonstrates example analysis capability",
                input_types=["text", "case"],
                output_types=["analysis_result"],
            ),
        ]
    
    async def health_check(self) -> bool:
        """Check if the agent is healthy and ready to process.
        
        Returns:
            True if healthy, False otherwise
        """
        return True
