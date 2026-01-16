# CRIS Architecture

> For complete technical details, see [GEMINI3_ADK_A2A_ARCHITECTURE.md](GEMINI3_ADK_A2A_ARCHITECTURE.md)

## System Overview

```mermaid
flowchart TB
    subgraph UI["🖥️ UI Layer - Streamlit"]
        Dashboard[Dashboard]
        Cases[Cases]
        Analysis[Analysis]
        Chat[Chat Interface]
    end
    
    subgraph Orchestration["🧠 Orchestration Layer"]
        Orch[Orchestrator Agent<br/>CRISOrchestratorAgent]
        
        subgraph OrchestratorFeatures[" "]
            QA[Query Analysis]
            AD[Agent Delegation A2A]
            RS[Result Synthesis]
            SM[Session Management]
        end
    end
    
    subgraph A2A["📡 A2A Protocol Layer"]
        Protocol{{"A2A Protocol"}}
    end
    
    subgraph Agents["🤖 Specialized Agents"]
        Link[Link Agent]
        Profiler[Profiler Agent]
        GeoIntel[Geo-Intel Agent]
        Witness[Witness Agent]
        Predictor[Predictor Agent]
        OSINT[OSINT Agent]
    end
    
    subgraph Data["💾 Data & Service Layer"]
        Neo4j[(Neo4j<br/>Knowledge Graph)]
        Chroma[(ChromaDB<br/>Vector Store)]
        LLM[LLM Service<br/>Gemini 3]
    end
    
    UI --> Orch
    Orch --> Protocol
    Protocol --> Link & Profiler & GeoIntel & Witness & Predictor & OSINT
    Agents --> Neo4j & Chroma & LLM
```

## Core Components

### 1. ADK Agent Base (`core/adk_agent.py`)
- `CRISADKAgent`: Base class for all agents
- `CRISOrchestratorAgent`: Orchestrator with delegation
- `AgentCard`: A2A capability advertisement

### 2. A2A Protocol (`core/a2a_server.py`)
- `A2AHandler`: Process incoming tasks
- `A2AClient`: Communicate with remote agents
- `A2ARegistry`: Local agent discovery

### 3. Data Layer
- **Neo4j**: Knowledge graph (entities, relationships)
- **ChromaDB**: Vector embeddings for semantic search

## Data Flow

```mermaid
sequenceDiagram
    participant U as User
    participant O as Orchestrator
    participant A2A as A2A Protocol
    participant Agents as Specialized Agents
    participant DB as Neo4j/ChromaDB
    
    U->>O: Query
    O->>O: Analyze Intent
    O->>A2A: Delegate Tasks
    
    par Parallel Processing
        A2A->>Agents: Link Agent Task
        A2A->>Agents: Profiler Agent Task
        A2A->>Agents: Other Agents...
    end
    
    Agents->>DB: Query Data
    DB-->>Agents: Results
    Agents-->>A2A: Agent Results
    A2A-->>O: Aggregated Results
    O->>O: Synthesize
    O-->>U: Final Response
```

## Extensibility

Create custom agents by extending `CRISADKAgent`:

```python
from core.adk_agent import CRISADKAgent, CRISToolResult

class MyAgent(CRISADKAgent):
    name = "my_agent"
    description = "Custom analysis agent"
    
    def get_tools(self):
        return [self.my_tool]
    
    async def my_tool(self, query: str) -> CRISToolResult:
        # Implementation
        return CRISToolResult(success=True, data={...})
```
