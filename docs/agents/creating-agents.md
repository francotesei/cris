# Creating Custom Agents

Extend CRIS with custom agents for specialized analysis tasks.

## Quick Start

```python
from core.adk_agent import CRISADKAgent, AgentRole, CRISToolResult
from core.a2a_server import A2AHandler, A2AAgentCard, A2ASkill, A2ARegistry
from core.registry import ComponentRegistry

@ComponentRegistry.register_agent("financial_agent")
class FinancialAgent(CRISADKAgent):
    name = "financial_agent"
    description = "Analyzes financial transactions for money laundering patterns."
    model = "gemini-2.0-flash"
    role = AgentRole.SPECIALIST
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._setup_a2a_handler()
    
    def _setup_a2a_handler(self):
        """Register with A2A protocol."""
        agent_card = A2AAgentCard(
            name=self.name,
            description=self.description,
            skills=[
                A2ASkill(
                    id="detect_laundering",
                    name="Detect Money Laundering",
                    description="Identify suspicious financial patterns"
                )
            ]
        )
        handler = A2AHandler(agent_card=agent_card, task_handler=self._handle_task)
        A2ARegistry().register(handler)
    
    def get_tools(self):
        return [self.analyze_transactions, self.detect_anomalies]
    
    async def analyze_transactions(
        self,
        transactions: list,
        threshold: float = 10000.0
    ) -> CRISToolResult:
        """Analyze transactions for suspicious patterns.
        
        Args:
            transactions: List of transaction records
            threshold: Amount threshold for flagging
            
        Returns:
            Analysis results with flagged transactions.
        """
        # Use Gemini 3 for analysis
        prompt = f"Analyze these transactions for suspicious patterns: {transactions}"
        response = self._client.models.generate_content(
            model=self._model,
            contents=prompt
        )
        
        return CRISToolResult(
            success=True,
            data={"analysis": response.text, "flagged_count": 0},
            confidence=0.85
        )
    
    async def detect_anomalies(self, account_id: str) -> CRISToolResult:
        """Detect anomalies in account activity."""
        # Implementation
        return CRISToolResult(success=True, data={})
```

## Key Components

### 1. Inherit from `CRISADKAgent`

```python
class MyAgent(CRISADKAgent):
    name = "my_agent"
    description = "What this agent does"
    model = "gemini-2.0-flash"  # Gemini 3
    role = AgentRole.SPECIALIST
```

### 2. Implement `get_tools()`

Return a list of tool functions:

```python
def get_tools(self):
    return [self.tool_one, self.tool_two]
```

### 3. Create Tools

Tools are async functions that return `CRISToolResult`:

```python
async def my_tool(self, param: str) -> CRISToolResult:
    """Tool description for Gemini.
    
    Args:
        param: What this parameter does
        
    Returns:
        Result with data and confidence.
    """
    return CRISToolResult(
        success=True,
        data={"result": "..."},
        confidence=0.9
    )
```

### 4. Register with A2A

Publish an Agent Card for discovery:

```python
def _setup_a2a_handler(self):
    agent_card = A2AAgentCard(
        name=self.name,
        description=self.description,
        skills=[A2ASkill(id="skill_id", name="Skill Name", description="...")]
    )
    handler = A2AHandler(agent_card=agent_card, task_handler=self._handle_task)
    A2ARegistry().register(handler)
```

## Best Practices

1. **Focused Tools**: Each tool should do one thing well
2. **Clear Docstrings**: Gemini uses docstrings to understand tools
3. **Confidence Scores**: Always provide confidence (0-1)
4. **Error Handling**: Return `success=False` with message on errors
5. **Async**: Use `async/await` for I/O operations

## Register with Orchestrator

Add your agent to `agents/__init__.py`:

```python
from agents.financial_agent import FinancialAgent

# In create_cris_system():
financial_agent = FinancialAgent()
orchestrator.register_agent(financial_agent)
```
