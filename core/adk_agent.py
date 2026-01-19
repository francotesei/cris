"""ADK Agent Base Classes.

Provides the foundation for building CRIS agents using Google's Agent Development Kit (ADK).
ADK enables powerful multi-agent orchestration with Gemini 3 as the reasoning engine.
"""

from abc import abstractmethod
from typing import Any, Callable, Dict, List, Optional, Type
from dataclasses import dataclass, field
from enum import Enum

from google import genai
from google.adk.agents import Agent, SequentialAgent, ParallelAgent, LoopAgent
from google.adk.tools import FunctionTool, ToolContext
from google.adk.sessions import InMemorySessionService, Session
from google.adk.runners import Runner
from google.genai import types as genai_types
from pydantic import BaseModel

from config.settings import get_settings
from utils.logger import get_logger


class AgentRole(str, Enum):
    """Defines the role of an agent in the CRIS system."""
    ORCHESTRATOR = "orchestrator"
    ANALYST = "analyst"
    SPECIALIST = "specialist"
    SUPPORT = "support"


@dataclass
class AgentCard:
    """A2A Agent Card for service discovery and capability advertisement.
    
    Agent Cards allow agents to discover each other and understand capabilities
    before delegating tasks via the A2A protocol.
    """
    name: str
    description: str
    version: str = "1.0.0"
    role: AgentRole = AgentRole.SPECIALIST
    capabilities: List[str] = field(default_factory=list)
    input_modes: List[str] = field(default_factory=lambda: ["text"])
    output_modes: List[str] = field(default_factory=lambda: ["text"])
    skills: List[Dict[str, Any]] = field(default_factory=list)
    endpoint: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to A2A-compatible dictionary format."""
        return {
            "name": self.name,
            "description": self.description,
            "version": self.version,
            "role": self.role.value,
            "capabilities": self.capabilities,
            "defaultInputModes": self.input_modes,
            "defaultOutputModes": self.output_modes,
            "skills": self.skills,
            "url": self.endpoint,
        }


class CRISToolResult(BaseModel):
    """Standard result format for CRIS tools."""
    success: bool
    data: Any
    message: Optional[str] = None
    confidence: float = 1.0


class CRISADKAgent:
    """Base class for CRIS agents built on Google ADK.
    
    This class wraps the ADK Agent with CRIS-specific functionality:
    - Automatic tool registration
    - A2A protocol support
    - Session management
    - Structured logging
    
    Example:
        class MyAgent(CRISADKAgent):
            name = "my_agent"
            description = "Does something useful"
            
            def get_tools(self):
                return [self.my_tool]
            
            @Tool
            def my_tool(self, query: str) -> str:
                return f"Processed: {query}"
    """
    
    name: str = "base_agent"
    description: str = "Base CRIS ADK Agent"
    model: str = "gemini-2.0-flash"  # Default to Gemini 3 (gemini-2.0-flash is the API name)
    role: AgentRole = AgentRole.SPECIALIST
    
    def __init__(
        self,
        model: Optional[str] = None,
        system_instruction: Optional[str] = None,
        **kwargs: Any
    ) -> None:
        """Initialize the ADK agent.
        
        Args:
            model: Override the default Gemini model.
            system_instruction: Custom system prompt for the agent.
            **kwargs: Additional configuration.
        """
        self.settings = get_settings()
        self.logger = get_logger(f"adk.{self.name}")
        
        # Configure Gemini client
        self._client = genai.Client(api_key=self.settings.google_api_key)
        
        # Set model (prefer Gemini 3 / 2.0-flash)
        self._model = model or self.model
        
        # Build system instruction
        self._system_instruction = system_instruction or self._build_system_instruction()
        
        # Initialize tools
        self._tools = self.get_tools()
        
        # Create the ADK Agent
        self._agent = Agent(
            name=self.name,
            model=self._model,
            description=self.description,
            instruction=self._system_instruction,
            tools=self._tools,
        )
        
        # Session management
        self._session_service = InMemorySessionService()
        self._runner: Optional[Runner] = None
        
        self.logger.info(f"Initialized ADK agent: {self.name} with model {self._model}")
    
    def _build_system_instruction(self) -> str:
        """Build the default system instruction for this agent."""
        return f"""You are {self.name}, a specialized AI agent in the CRIS (Criminal Reasoning Intelligence System).

Your role: {self.description}

Guidelines:
- Always provide accurate, evidence-based analysis
- Clearly state confidence levels for your assessments
- Flag any ethical concerns or limitations
- Collaborate effectively with other agents when needed
- Maintain chain of custody and audit trail awareness

Available tools will help you accomplish your tasks. Use them appropriately."""
    
    @abstractmethod
    def get_tools(self) -> List[Callable]:
        """Return the list of tools available to this agent.
        
        Subclasses must implement this to provide agent-specific tools.
        
        Returns:
            List of tool functions decorated with @Tool.
        """
        pass
    
    def get_agent_card(self) -> AgentCard:
        """Generate the A2A Agent Card for this agent.
        
        Returns:
            AgentCard with capability information.
        """
        return AgentCard(
            name=self.name,
            description=self.description,
            role=self.role,
            capabilities=[t.__name__ for t in self._tools if hasattr(t, '__name__')],
            skills=[
                {
                    "id": f"{self.name}_{t.__name__}",
                    "name": t.__name__,
                    "description": t.__doc__ or "No description",
                }
                for t in self._tools if hasattr(t, '__name__')
            ]
        )
    
    @property
    def adk_agent(self) -> Agent:
        """Access the underlying ADK Agent instance."""
        return self._agent
    
    async def create_session(self, session_id: Optional[str] = None, user_id: str = "default") -> Session:
        """Create or retrieve a session for conversation state.
        
        Args:
            session_id: Optional existing session ID.
            user_id: User identifier for the session.
            
        Returns:
            Session object for state management.
        """
        if session_id:
            session = self._session_service.get_session(
                app_name=self.name,
                user_id=user_id,
                session_id=session_id
            )
            if session:
                return session
        
        return self._session_service.create_session(
            app_name=self.name,
            user_id=user_id
        )
    
    async def run(
        self,
        query: str,
        session_id: Optional[str] = None,
        user_id: str = "default",
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Execute the agent with a query.
        
        Args:
            query: The user query or task.
            session_id: Optional session for conversation continuity.
            user_id: User identifier.
            context: Additional context to pass to the agent.
            
        Returns:
            Dictionary with agent response and metadata.
        """
        session = await self.create_session(session_id, user_id)
        
        # Create runner if not exists
        if not self._runner:
            self._runner = Runner(
                agent=self._agent,
                app_name=self.name,
                session_service=self._session_service
            )
        
        self.logger.info(f"Running query: {query[:100]}...")
        
        # Execute and collect results
        results = []
        async for event in self._runner.run_async(
            user_id=user_id,
            session_id=session.id,
            new_message=genai_types.Content(
                role="user",
                parts=[genai_types.Part(text=query)]
            )
        ):
            if hasattr(event, 'content') and event.content:
                results.append(event.content)
        
        # Extract final response
        final_response = ""
        for content in results:
            if hasattr(content, 'parts'):
                for part in content.parts:
                    if hasattr(part, 'text'):
                        final_response += part.text
        
        return {
            "agent": self.name,
            "response": final_response,
            "session_id": session.id,
            "context": context or {}
        }
    
    async def health_check(self) -> bool:
        """Verify the agent is operational.
        
        Returns:
            True if healthy, False otherwise.
        """
        try:
            # Simple test to verify Gemini connectivity
            response = self._client.models.generate_content(
                model=self._model,
                contents="Reply with 'OK' if you can read this."
            )
            return "OK" in response.text
        except Exception as e:
            self.logger.error(f"Health check failed: {e}")
            return False


class CRISOrchestratorAgent(CRISADKAgent):
    """Specialized orchestrator agent that coordinates other agents.
    
    Uses ADK's built-in agent delegation capabilities combined with
    A2A protocol for cross-agent communication.
    """
    
    role = AgentRole.ORCHESTRATOR
    
    def __init__(
        self,
        sub_agents: Optional[List[CRISADKAgent]] = None,
        **kwargs: Any
    ) -> None:
        """Initialize the orchestrator.
        
        Args:
            sub_agents: List of agents this orchestrator can delegate to.
            **kwargs: Additional configuration.
        """
        self._sub_agents: Dict[str, CRISADKAgent] = {}
        super().__init__(**kwargs)
        
        # Register sub-agents
        if sub_agents:
            for agent in sub_agents:
                self.register_agent(agent)
    
    def register_agent(self, agent: CRISADKAgent) -> None:
        """Register a sub-agent for delegation.
        
        Args:
            agent: The agent to register.
        """
        self._sub_agents[agent.name] = agent
        self.logger.info(f"Registered sub-agent: {agent.name}")
    
    def get_registered_agents(self) -> Dict[str, AgentCard]:
        """Get all registered agents and their capabilities.
        
        Returns:
            Dictionary mapping agent names to their Agent Cards.
        """
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
        """Delegate a task to a specific sub-agent.
        
        Args:
            agent_name: Name of the agent to delegate to.
            query: The task/query to send.
            context: Additional context.
            
        Returns:
            Result from the delegated agent.
        """
        if agent_name not in self._sub_agents:
            return {
                "success": False,
                "error": f"Agent '{agent_name}' not found"
            }
        
        agent = self._sub_agents[agent_name]
        self.logger.info(f"Delegating to {agent_name}: {query[:50]}...")
        
        return await agent.run(query, context=context)


def create_tool(
    name: str,
    description: str,
    func: Callable,
    parameters: Optional[Dict[str, Any]] = None
) -> FunctionTool:
    """Helper to create ADK tools with proper metadata.
    
    Args:
        name: Tool name.
        description: What the tool does.
        func: The function to execute.
        parameters: JSON schema for parameters.
        
    Returns:
        Configured ADK FunctionTool.
    """
    func.__name__ = name
    func.__doc__ = description
    return FunctionTool(func=func)
