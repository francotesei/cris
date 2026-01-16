"""Base Agent Abstractions.

Defines the interface and common functionality for all CRIS agents.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field

from utils.logger import get_logger


class AgentCapability(BaseModel):
    """Describes what an agent can do."""
    name: str
    description: str
    input_types: List[str]
    output_types: List[str]


class AgentInput(BaseModel):
    """Standard input for agent processing."""
    query: str
    case_id: Optional[str] = None
    context: Dict[str, Any] = {}
    parameters: Dict[str, Any] = {}


class AgentOutput(BaseModel):
    """Standard output for agent processing."""
    agent_name: str
    success: bool
    data: Any
    confidence: float = Field(default=1.0, ge=0.0, le=1.0)
    message: Optional[str] = None
    metadata: Dict[str, Any] = {}


class BaseAgent(ABC):
    """Abstract base class for all CRIS agents.
    
    Attributes:
        name: Unique identifier for the agent.
        description: Human-readable description of the agent.
    """
    
    name: str
    description: str
    
    def __init__(self, llm_service: Any = None, **kwargs: Any) -> None:
        """Initialize the agent.
        
        Args:
            llm_service: The LLM service for AI operations.
            **kwargs: Additional configuration for the agent.
        """
        self.llm_service = llm_service
        self.logger = get_logger(f"agent.{self.name}")
        self.config = kwargs

    @abstractmethod
    async def process(self, input: AgentInput) -> AgentOutput:
        """Process the input and return analysis results.
        
        Args:
            input: The agent input containing query and context.
            
        Returns:
            An AgentOutput object.
        """
        pass

    @abstractmethod
    def get_capabilities(self) -> List[AgentCapability]:
        """Return the list of capabilities provided by this agent.
        
        Returns:
            A list of AgentCapability objects.
        """
        pass

    async def health_check(self) -> bool:
        """Verify the agent is healthy and its dependencies are available.
        
        Returns:
            True if healthy, False otherwise.
        """
        return True
