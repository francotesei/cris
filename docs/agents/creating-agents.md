# Creating Custom Agents

One of CRIS's greatest strengths is its extensibility. You can create specialized agents for new investigative tasks (e.g., Financial Analysis, Forensics, Cyber Intelligence).

## 🛠️ Step-by-Step Guide

### 1. Inherit from `BaseAgent`

Create a new file in `agents/` or in your plugin directory.

```python
from core.base_agent import BaseAgent, AgentInput, AgentOutput, AgentCapability
from core.registry import ComponentRegistry

@ComponentRegistry.register_agent("financial_agent")
class FinancialAgent(BaseAgent):
    name = "financial_agent"
    description = "Analyzes bank records and money laundering patterns."
    
    async def process(self, input: AgentInput) -> AgentOutput:
        # 1. Access input query and parameters
        query = input.query
        
        # 2. Perform your analysis logic
        # You can access self.llm_service if needed
        
        # 3. Return a standardized output
        return AgentOutput(
            agent_name=self.name,
            success=True,
            data={"transactions": [...], "anomalies": ["Rapid transfers to offshore"]}
        )

    def get_capabilities(self) -> list[AgentCapability]:
        return [
            AgentCapability(
                name="money_laundering_detection",
                description="Detects suspicious financial flows",
                input_types=["bank_records"],
                output_types=["anomaly_report"]
            )
        ]
```

### 2. Register the Agent

The `@ComponentRegistry.register_agent("name")` decorator ensures the Orchestrator can find and activate your agent.

### 3. Implement Capabilities

The `get_capabilities()` method helps the Orchestrator understand when it should use your agent.

## 💡 Best Practices

- **Atomic Tasks**: Keep agents focused on a single domain.
- **Async First**: Use `async/await` for database or API calls to avoid blocking the system.
- **Logging**: Use `self.logger.info()` or `self.logger.error()` for better debugging in the dashboard.
- **Confidence Scores**: Always provide a confidence score (0-1) in your `AgentOutput`.
- **Structured Data**: Prefer returning Pydantic models or clean dictionaries in the `data` field.
