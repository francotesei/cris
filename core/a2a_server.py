"""A2A (Agent-to-Agent) Protocol Server.

Implements the A2A protocol for inter-agent communication and discovery.
This enables CRIS agents to collaborate, delegate tasks, and share context
in a standardized way.

Reference: https://a2a-protocol.org/
"""

import asyncio
import json
import uuid
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, AsyncIterator, Callable, Dict, List, Optional

from pydantic import BaseModel, Field
import httpx

from utils.logger import get_logger


class TaskState(str, Enum):
    """A2A Task lifecycle states."""
    SUBMITTED = "submitted"
    WORKING = "working"
    INPUT_REQUIRED = "input-required"
    COMPLETED = "completed"
    CANCELED = "canceled"
    FAILED = "failed"


class MessageRole(str, Enum):
    """Message sender role."""
    USER = "user"
    AGENT = "agent"


class ContentPart(BaseModel):
    """A single part of message content."""
    type: str = "text"
    text: Optional[str] = None
    data: Optional[Dict[str, Any]] = None
    mime_type: Optional[str] = None


class Message(BaseModel):
    """A2A Message format."""
    role: MessageRole
    parts: List[ContentPart]
    metadata: Dict[str, Any] = Field(default_factory=dict)


class Artifact(BaseModel):
    """Output artifact from a task."""
    name: str
    description: Optional[str] = None
    parts: List[ContentPart]
    index: int = 0
    append: bool = False
    last_chunk: bool = True


class TaskStatus(BaseModel):
    """Current status of an A2A task."""
    state: TaskState
    message: Optional[Message] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class Task(BaseModel):
    """A2A Task representation."""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    session_id: Optional[str] = None
    status: TaskStatus = Field(default_factory=lambda: TaskStatus(state=TaskState.SUBMITTED))
    artifacts: List[Artifact] = Field(default_factory=list)
    history: List[Message] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict)


class TaskSendParams(BaseModel):
    """Parameters for sending a task to an agent."""
    id: str
    session_id: Optional[str] = None
    message: Message
    accept_streaming: bool = True
    metadata: Dict[str, Any] = Field(default_factory=dict)


class A2ASkill(BaseModel):
    """Skill definition for Agent Card."""
    id: str
    name: str
    description: str
    tags: List[str] = Field(default_factory=list)
    examples: List[str] = Field(default_factory=list)
    input_modes: List[str] = Field(default_factory=lambda: ["text"])
    output_modes: List[str] = Field(default_factory=lambda: ["text"])


class A2AAgentCard(BaseModel):
    """A2A Agent Card for capability advertisement."""
    name: str
    description: str
    url: Optional[str] = None
    version: str = "1.0.0"
    protocol_version: str = "0.2"
    capabilities: Dict[str, bool] = Field(default_factory=lambda: {
        "streaming": True,
        "pushNotifications": False,
        "stateTransitionHistory": True,
    })
    default_input_modes: List[str] = Field(default_factory=lambda: ["text"])
    default_output_modes: List[str] = Field(default_factory=lambda: ["text"])
    skills: List[A2ASkill] = Field(default_factory=list)
    
    class Config:
        populate_by_name = True


class A2AHandler:
    """Handler for processing A2A requests.
    
    This class processes incoming A2A tasks and delegates them to
    the appropriate CRIS agent.
    """
    
    def __init__(
        self,
        agent_card: A2AAgentCard,
        task_handler: Callable[[Task, Message], AsyncIterator[Dict[str, Any]]]
    ) -> None:
        """Initialize the A2A handler.
        
        Args:
            agent_card: The agent's capability card.
            task_handler: Async generator function to process tasks.
        """
        self.agent_card = agent_card
        self.task_handler = task_handler
        self.tasks: Dict[str, Task] = {}
        self.logger = get_logger(f"a2a.{agent_card.name}")
    
    async def handle_task_send(self, params: TaskSendParams) -> Task:
        """Handle a new task submission.
        
        Args:
            params: Task parameters from the client.
            
        Returns:
            The created or updated Task.
        """
        # Get or create task
        task = self.tasks.get(params.id)
        if not task:
            task = Task(
                id=params.id,
                session_id=params.session_id,
                metadata=params.metadata
            )
            self.tasks[params.id] = task
        
        # Add message to history
        task.history.append(params.message)
        task.status = TaskStatus(state=TaskState.WORKING)
        
        self.logger.info(f"Processing task {task.id}")
        
        # Process the task
        try:
            async for event in self.task_handler(task, params.message):
                if event.get("type") == "artifact":
                    artifact = Artifact(**event["artifact"])
                    task.artifacts.append(artifact)
                elif event.get("type") == "status":
                    task.status = TaskStatus(
                        state=TaskState(event["state"]),
                        message=Message(**event["message"]) if event.get("message") else None
                    )
            
            # Mark completed if not already in terminal state
            if task.status.state == TaskState.WORKING:
                task.status = TaskStatus(state=TaskState.COMPLETED)
                
        except Exception as e:
            self.logger.error(f"Task {task.id} failed: {e}")
            task.status = TaskStatus(
                state=TaskState.FAILED,
                message=Message(
                    role=MessageRole.AGENT,
                    parts=[ContentPart(text=str(e))]
                )
            )
        
        return task
    
    async def handle_task_send_streaming(
        self,
        params: TaskSendParams
    ) -> AsyncIterator[Dict[str, Any]]:
        """Handle a task with streaming response.
        
        Args:
            params: Task parameters from the client.
            
        Yields:
            Streaming events (status updates, artifacts, etc.)
        """
        task = self.tasks.get(params.id)
        if not task:
            task = Task(
                id=params.id,
                session_id=params.session_id,
                metadata=params.metadata
            )
            self.tasks[params.id] = task
        
        task.history.append(params.message)
        task.status = TaskStatus(state=TaskState.WORKING)
        
        yield {
            "type": "status",
            "task_id": task.id,
            "state": TaskState.WORKING.value
        }
        
        try:
            async for event in self.task_handler(task, params.message):
                yield event
            
            task.status = TaskStatus(state=TaskState.COMPLETED)
            yield {
                "type": "status",
                "task_id": task.id,
                "state": TaskState.COMPLETED.value
            }
            
        except Exception as e:
            task.status = TaskStatus(state=TaskState.FAILED)
            yield {
                "type": "error",
                "task_id": task.id,
                "error": str(e)
            }
    
    def get_task(self, task_id: str) -> Optional[Task]:
        """Retrieve a task by ID.
        
        Args:
            task_id: The task identifier.
            
        Returns:
            The Task if found, None otherwise.
        """
        return self.tasks.get(task_id)
    
    def cancel_task(self, task_id: str) -> bool:
        """Cancel a running task.
        
        Args:
            task_id: The task to cancel.
            
        Returns:
            True if canceled, False if not found or already complete.
        """
        task = self.tasks.get(task_id)
        if not task:
            return False
        
        if task.status.state in [TaskState.COMPLETED, TaskState.FAILED, TaskState.CANCELED]:
            return False
        
        task.status = TaskStatus(state=TaskState.CANCELED)
        return True


class A2AClient:
    """Client for communicating with remote A2A agents.
    
    Enables CRIS agents to discover and delegate tasks to other agents
    via the A2A protocol.
    """
    
    def __init__(self, timeout: float = 30.0) -> None:
        """Initialize the A2A client.
        
        Args:
            timeout: Request timeout in seconds.
        """
        self.timeout = timeout
        self.logger = get_logger("a2a.client")
        self._http_client = httpx.AsyncClient(timeout=timeout)
        self._agent_cards: Dict[str, A2AAgentCard] = {}
    
    async def discover_agent(self, url: str) -> A2AAgentCard:
        """Discover an agent's capabilities via its Agent Card.
        
        Args:
            url: Base URL of the A2A agent.
            
        Returns:
            The agent's capability card.
        """
        card_url = f"{url.rstrip('/')}/.well-known/agent.json"
        
        try:
            response = await self._http_client.get(card_url)
            response.raise_for_status()
            card_data = response.json()
            card = A2AAgentCard(**card_data)
            self._agent_cards[url] = card
            self.logger.info(f"Discovered agent: {card.name} at {url}")
            return card
        except Exception as e:
            self.logger.error(f"Failed to discover agent at {url}: {e}")
            raise
    
    async def send_task(
        self,
        url: str,
        message: str,
        task_id: Optional[str] = None,
        session_id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Task:
        """Send a task to a remote A2A agent.
        
        Args:
            url: Base URL of the target agent.
            message: The message/query to send.
            task_id: Optional task ID (generated if not provided).
            session_id: Optional session for conversation continuity.
            metadata: Additional metadata.
            
        Returns:
            The completed Task with results.
        """
        task_url = f"{url.rstrip('/')}/tasks/send"
        
        params = TaskSendParams(
            id=task_id or str(uuid.uuid4()),
            session_id=session_id,
            message=Message(
                role=MessageRole.USER,
                parts=[ContentPart(text=message)]
            ),
            accept_streaming=False,
            metadata=metadata or {}
        )
        
        try:
            response = await self._http_client.post(
                task_url,
                json=params.model_dump(mode="json")
            )
            response.raise_for_status()
            return Task(**response.json())
        except Exception as e:
            self.logger.error(f"Failed to send task to {url}: {e}")
            raise
    
    async def send_task_streaming(
        self,
        url: str,
        message: str,
        task_id: Optional[str] = None,
        session_id: Optional[str] = None
    ) -> AsyncIterator[Dict[str, Any]]:
        """Send a task with streaming response.
        
        Args:
            url: Base URL of the target agent.
            message: The message/query to send.
            task_id: Optional task ID.
            session_id: Optional session ID.
            
        Yields:
            Streaming events from the agent.
        """
        task_url = f"{url.rstrip('/')}/tasks/sendSubscribe"
        
        params = TaskSendParams(
            id=task_id or str(uuid.uuid4()),
            session_id=session_id,
            message=Message(
                role=MessageRole.USER,
                parts=[ContentPart(text=message)]
            ),
            accept_streaming=True
        )
        
        async with self._http_client.stream(
            "POST",
            task_url,
            json=params.model_dump(mode="json")
        ) as response:
            async for line in response.aiter_lines():
                if line.startswith("data: "):
                    data = json.loads(line[6:])
                    yield data
    
    async def get_task_status(self, url: str, task_id: str) -> Task:
        """Get the current status of a task.
        
        Args:
            url: Base URL of the agent.
            task_id: The task identifier.
            
        Returns:
            The Task with current status.
        """
        status_url = f"{url.rstrip('/')}/tasks/get"
        
        response = await self._http_client.post(
            status_url,
            json={"id": task_id}
        )
        response.raise_for_status()
        return Task(**response.json())
    
    async def close(self) -> None:
        """Close the HTTP client."""
        await self._http_client.aclose()


class A2ARegistry:
    """Registry for local A2A agents.
    
    Manages agent registration and discovery within a single CRIS instance.
    """
    
    _instance: Optional["A2ARegistry"] = None
    
    def __new__(cls) -> "A2ARegistry":
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._handlers: Dict[str, A2AHandler] = {}
            cls._instance.logger = get_logger("a2a.registry")
        return cls._instance
    
    def register(self, handler: A2AHandler) -> None:
        """Register an A2A handler.
        
        Args:
            handler: The handler to register.
        """
        self._handlers[handler.agent_card.name] = handler
        self.logger.info(f"Registered A2A handler: {handler.agent_card.name}")
    
    def get_handler(self, name: str) -> Optional[A2AHandler]:
        """Get a handler by agent name.
        
        Args:
            name: The agent name.
            
        Returns:
            The handler if found.
        """
        return self._handlers.get(name)
    
    def list_agents(self) -> List[A2AAgentCard]:
        """List all registered agent cards.
        
        Returns:
            List of agent capability cards.
        """
        return [h.agent_card for h in self._handlers.values()]
    
    async def route_task(
        self,
        agent_name: str,
        message: str,
        task_id: Optional[str] = None
    ) -> Task:
        """Route a task to a local agent.
        
        Args:
            agent_name: Target agent name.
            message: The message to send.
            task_id: Optional task ID.
            
        Returns:
            The completed Task.
        """
        handler = self._handlers.get(agent_name)
        if not handler:
            raise ValueError(f"Agent '{agent_name}' not found in registry")
        
        params = TaskSendParams(
            id=task_id or str(uuid.uuid4()),
            message=Message(
                role=MessageRole.USER,
                parts=[ContentPart(text=message)]
            )
        )
        
        return await handler.handle_task_send(params)
