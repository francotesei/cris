"""Multi-Provider Agent Base Class.

Provides a base class for CRIS agents that works with any LLM provider
(Gemini, Ollama, OpenAI, Anthropic) without requiring Google ADK.

This is an alternative to CRISADKAgent for when you want to use
local models via Ollama or other providers.
"""

from abc import abstractmethod
from typing import Any, Callable, Dict, List, Optional, TYPE_CHECKING
from dataclasses import dataclass, field
from enum import Enum

from pydantic import BaseModel

from config.settings import get_settings
from config.model_config import get_agent_config
from utils.logger import get_logger

# Lazy import to avoid circular dependency
if TYPE_CHECKING:
    from services.llm_service import LLMService


class AgentRole(str, Enum):
    """Defines the role of an agent in the CRIS system."""
    ORCHESTRATOR = "orchestrator"
    ANALYST = "analyst"
    SPECIALIST = "specialist"
    SUPPORT = "support"


@dataclass
class AgentCard:
    """Agent capability card for discovery."""
    name: str
    description: str
    version: str = "1.0.0"
    role: AgentRole = AgentRole.SPECIALIST
    capabilities: List[str] = field(default_factory=list)
    provider: str = "ollama"
    model: str = "llama3.2"
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "description": self.description,
            "version": self.version,
            "role": self.role.value,
            "capabilities": self.capabilities,
            "provider": self.provider,
            "model": self.model,
        }


class ToolResult(BaseModel):
    """Standard result format for agent tools."""
    success: bool
    data: Any
    message: Optional[str] = None
    confidence: float = 1.0


class MultiProviderAgent:
    """Base class for CRIS agents that work with any LLM provider.
    
    Unlike CRISADKAgent which requires Google ADK and Gemini,
    this class works with any provider supported by LLMService:
    - Gemini (cloud)
    - Ollama (local)
    - OpenAI (cloud)
    - Anthropic (cloud)
    
    Example:
        class MyAgent(MultiProviderAgent):
            name = "my_agent"
            description = "Does something useful"
            
            def get_tools(self):
                return [self.my_tool]
            
            async def my_tool(self, query: str) -> ToolResult:
                return ToolResult(success=True, data={"result": query})
    """
    
    name: str = "base_agent"
    description: str = "Base Multi-Provider Agent"
    role: AgentRole = AgentRole.SPECIALIST
    
    def __init__(
        self,
        system_instruction: Optional[str] = None,
        **kwargs: Any
    ) -> None:
        """Initialize the agent with configured LLM provider.
        
        Args:
            system_instruction: Custom system prompt for the agent.
            **kwargs: Additional configuration.
        """
        self.settings = get_settings()
        self.logger = get_logger(f"agent.{self.name}")
        
        # Get agent-specific model configuration (from CRIS_ENV + models.yml)
        self._config = get_agent_config(self.name)
        self._provider = self._config["provider"]
        self._model = self._config["model"]
        self._temperature = self._config["temperature"]
        self._max_tokens = self._config["max_tokens"]
        
        # Initialize LLM service (lazy import to avoid circular dependency)
        from services.llm_service import LLMService
        self._llm = LLMService()
        
        # Build system instruction
        self._system_instruction = system_instruction or self._build_system_instruction()
        
        # Initialize tools
        self._tools = self.get_tools()
        
        self.logger.info(
            f"Initialized {self.name} with {self._provider}/{self._model}"
        )
    
    def _build_system_instruction(self) -> str:
        """Build the default system instruction for this agent."""
        return f"""You are {self.name}, a specialized AI agent in the CRIS (Criminal Reasoning Intelligence System).

Your role: {self.description}

Guidelines:
- Always provide accurate, evidence-based analysis
- Clearly state confidence levels for your assessments
- Flag any ethical concerns or limitations
- Maintain professional investigative standards
- Provide actionable insights when possible

Respond in a clear, structured format appropriate for law enforcement use."""
    
    @abstractmethod
    def get_tools(self) -> List[Callable]:
        """Return the list of tools available to this agent.
        
        Subclasses must implement this to provide agent-specific tools.
        
        Returns:
            List of async tool functions.
        """
        pass
    
    def get_agent_card(self) -> AgentCard:
        """Generate the Agent Card for this agent."""
        return AgentCard(
            name=self.name,
            description=self.description,
            role=self.role,
            capabilities=[t.__name__ for t in self._tools if hasattr(t, '__name__')],
            provider=self._provider,
            model=self._model,
        )
    
    async def run(
        self,
        query: str,
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Execute the agent with a query.
        
        Args:
            query: The user query or task.
            context: Additional context to pass to the agent.
            
        Returns:
            Dictionary with agent response and metadata.
        """
        self.logger.info(f"Processing query: {query[:100]}...")
        
        # Build context-aware prompt
        context_str = ""
        if context:
            context_str = f"\n\nContext:\n{self._format_context(context)}"
        
        full_prompt = f"{query}{context_str}"
        
        try:
            # Generate response using LLM service
            response = await self._llm.generate(
                prompt=full_prompt,
                system_instruction=self._system_instruction,
                temperature=self._temperature,
                max_tokens=self._max_tokens
            )
            
            return {
                "agent": self.name,
                "response": response,
                "provider": self._provider,
                "model": self._model,
                "context": context or {}
            }
            
        except Exception as e:
            self.logger.error(f"Agent execution failed: {e}")
            return {
                "agent": self.name,
                "response": f"Error: {str(e)}",
                "error": True,
                "provider": self._provider,
                "model": self._model,
            }
    
    def _format_context(self, context: Dict[str, Any]) -> str:
        """Format context dictionary for inclusion in prompt."""
        lines = []
        for key, value in context.items():
            if isinstance(value, dict):
                lines.append(f"- {key}:")
                for k, v in value.items():
                    lines.append(f"    {k}: {v}")
            else:
                lines.append(f"- {key}: {value}")
        return "\n".join(lines)
    
    async def health_check(self) -> bool:
        """Verify the agent is operational.
        
        Returns:
            True if healthy, False otherwise.
        """
        try:
            response = await self._llm.generate(
                prompt="Reply with exactly 'OK' if you can read this.",
                max_tokens=10
            )
            return "OK" in response.upper()
        except Exception as e:
            self.logger.error(f"Health check failed: {e}")
            return False


class MultiProviderOrchestrator(MultiProviderAgent):
    """Orchestrator agent that coordinates other agents.
    
    Works with any LLM provider for task routing and synthesis.
    """
    
    role = AgentRole.ORCHESTRATOR
    
    def __init__(
        self,
        sub_agents: Optional[List[MultiProviderAgent]] = None,
        **kwargs: Any
    ) -> None:
        """Initialize the orchestrator.
        
        Args:
            sub_agents: List of agents this orchestrator can delegate to.
            **kwargs: Additional configuration.
        """
        self._sub_agents: Dict[str, MultiProviderAgent] = {}
        super().__init__(**kwargs)
        
        if sub_agents:
            for agent in sub_agents:
                self.register_agent(agent)
    
    def register_agent(self, agent: MultiProviderAgent) -> None:
        """Register a sub-agent for delegation."""
        self._sub_agents[agent.name] = agent
        self.logger.info(f"Registered sub-agent: {agent.name}")
    
    def get_registered_agents(self) -> Dict[str, AgentCard]:
        """Get all registered agents and their capabilities."""
        return {
            name: agent.get_agent_card()
            for name, agent in self._sub_agents.items()
        }
    
    async def delegate(
        self,
        agent_name: str,
        query: str,
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Delegate a task to a specific sub-agent."""
        if agent_name not in self._sub_agents:
            return {
                "success": False,
                "error": f"Agent '{agent_name}' not found. Available: {list(self._sub_agents.keys())}"
            }
        
        agent = self._sub_agents[agent_name]
        self.logger.info(f"Delegating to {agent_name}: {query[:50]}...")
        
        return await agent.run(query, context=context)
