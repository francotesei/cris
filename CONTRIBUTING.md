# Contributing to CRIS

Thank you for contributing! 🎉

## Code of Conduct

See [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md).

## Development Setup

```bash
git clone https://github.com/YOUR_USERNAME/cris.git
cd cris
uv sync --all-extras
docker-compose up -d
cp .env.example .env
# Add GOOGLE_API_KEY to .env
```

## Pull Request Process

1. Fork and create branch from `main`
2. Make changes with clear commits
3. Add tests for new functionality
4. Run tests: `uv run pytest`
5. Lint: `uv run ruff check . && uv run black --check .`
6. Submit PR with description

## Creating Agents

New agents should:

1. Extend `CRISADKAgent`
2. Use Gemini 3 (`gemini-2.0-flash`)
3. Implement `get_tools()` with specialized tools
4. Register with A2A protocol
5. Include docstrings for all tools

Example:

```python
from core.adk_agent import CRISADKAgent, CRISToolResult

class MyAgent(CRISADKAgent):
    name = "my_agent"
    description = "What it does"
    
    def get_tools(self):
        return [self.my_tool]
    
    async def my_tool(self, param: str) -> CRISToolResult:
        """Tool description."""
        return CRISToolResult(success=True, data={})
```

## Coding Standards

- Python: PEP 8, Black formatting, Ruff linting
- Type hints required
- Google-style docstrings
- Async for I/O operations
- Tests with pytest

## Project Structure

```
cris/
├── agents/      # ADK agents
├── core/        # Base classes (adk_agent, a2a_server)
├── config/      # Settings and prompts
├── database/    # Neo4j, ChromaDB
├── models/      # Pydantic models
├── services/    # External services
├── ui/          # Streamlit components
└── tests/       # Test suite
```

## Questions?

Open an issue with the "question" label.
