# Data Models

CRIS uses Pydantic models for validation.

## Core Models

### CRISToolResult
Standard tool output format:

```python
class CRISToolResult(BaseModel):
    success: bool
    data: Any
    message: Optional[str] = None
    confidence: float = 1.0
```

### AgentCard
A2A capability advertisement:

```python
@dataclass
class AgentCard:
    name: str
    description: str
    version: str = "1.0.0"
    role: AgentRole
    capabilities: List[str]
    skills: List[Dict[str, Any]]
```

## Case Models (`models/case.py`)

```python
class Case(BaseModel):
    id: str
    title: str
    status: str  # open, closed, cold
    crime_type: str
    priority: int  # 1-5
```

## Person Models (`models/person.py`)

```python
class Person(BaseModel):
    id: str
    name: str
    alias: List[str]
    role: str  # victim, suspect, witness
    risk_score: float  # 0-1
```

## Evidence Models (`models/evidence.py`)

```python
class Evidence(BaseModel):
    id: str
    type: str  # document, photo, video
    extracted_text: str
    chain_of_custody: List[str]
```

## A2A Models (`core/a2a_server.py`)

```python
class Task(BaseModel):
    id: str
    session_id: Optional[str]
    status: TaskStatus
    artifacts: List[Artifact]
    history: List[Message]

class Message(BaseModel):
    role: MessageRole  # user, agent
    parts: List[ContentPart]
```
