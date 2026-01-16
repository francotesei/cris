# Contributing to CRIS

First off, thank you for considering contributing to CRIS! It's people like you that make CRIS such a great tool for criminal intelligence analysis.

## Code of Conduct

This project and everyone participating in it is governed by our [Code of Conduct](CODE_OF_CONDUCT.md). By participating, you are expected to uphold this code.

## How Can I Contribute?

### Reporting Bugs

Before creating bug reports, please check the existing issues to avoid duplicates. When you create a bug report, include as many details as possible:

- **Use a clear and descriptive title**
- **Describe the exact steps to reproduce the problem**
- **Provide specific examples** (code snippets, sample data)
- **Describe the behavior you observed and what you expected**
- **Include logs and error messages**
- **Specify your environment** (OS, Python version, dependencies)

### Suggesting Enhancements

Enhancement suggestions are tracked as GitHub issues. When creating an enhancement suggestion:

- **Use a clear and descriptive title**
- **Provide a detailed description of the proposed enhancement**
- **Explain why this enhancement would be useful**
- **List any alternatives you've considered**

### Pull Requests

1. **Fork the repo** and create your branch from `main`
2. **Install dependencies**: `uv sync --all-extras`
3. **Make your changes** with clear, descriptive commits
4. **Add tests** for any new functionality
5. **Ensure tests pass**: `uv run pytest`
6. **Lint your code**: `uv run ruff check . && uv run black --check .`
7. **Update documentation** if needed
8. **Submit your PR** with a clear description

## Development Setup

```bash
# Clone your fork
git clone https://github.com/YOUR_USERNAME/cris.git
cd cris

# Install uv if you haven't
curl -LsSf https://astral.sh/uv/install.sh | sh

# Install dependencies
uv sync --all-extras

# Start Neo4j
docker-compose up -d

# Copy environment config
cp .env.example .env
# Edit .env with your API keys

# Run the application
uv run streamlit run app.py
```

## Project Structure

```
cris/
├── agents/          # AI agents for analysis
├── config/          # Configuration and settings
├── core/            # Base classes and abstractions
├── database/        # Neo4j and vector store clients
├── models/          # Pydantic data models
├── processors/      # Document and data processors
├── services/        # External service integrations
├── ui/              # Streamlit UI components
├── plugins/         # User-defined plugins
└── tests/           # Test suite
```

## Coding Standards

### Python Style

- Follow [PEP 8](https://pep8.org/)
- Use [Black](https://black.readthedocs.io/) for formatting
- Use [Ruff](https://docs.astral.sh/ruff/) for linting
- Maximum line length: 100 characters

### Type Hints

Always use type hints:

```python
async def process_case(case_id: str, options: dict[str, Any] | None = None) -> CaseResult:
    ...
```

### Docstrings

Use Google-style docstrings:

```python
def analyze_evidence(evidence: Evidence, depth: int = 1) -> AnalysisResult:
    """Analyze evidence and return structured results.
    
    Args:
        evidence: The evidence object to analyze
        depth: Analysis depth level (1-3)
        
    Returns:
        AnalysisResult containing findings and confidence scores
        
    Raises:
        ValueError: If evidence type is not supported
    """
```

### Async Code

- Use `async/await` for I/O operations
- Prefer `asyncio.gather()` for parallel operations
- Always handle exceptions in async code

### Testing

- Write tests for all new functionality
- Use pytest fixtures for common setup
- Aim for >80% code coverage
- Test both success and error cases

```python
@pytest.mark.asyncio
async def test_link_agent_finds_connections(mock_neo4j_client):
    agent = LinkAgent(neo4j_client=mock_neo4j_client)
    result = await agent.find_connections("CASE-001")
    assert result.success
    assert len(result.connections) > 0
```

## Creating Plugins

See [plugins/README.md](plugins/README.md) for detailed plugin development guide.

## Documentation

- Update relevant docs when changing functionality
- Use clear, concise language
- Include code examples
- Build docs locally: `uv run mkdocs serve`

## Release Process

1. Update `CHANGELOG.md` with changes
2. Bump version in `pyproject.toml`
3. Create a pull request to `main`
4. After merge, create a GitHub release
5. CI will publish to PyPI automatically

## Questions?

Feel free to open an issue with the "question" label or reach out to maintainers.

Thank you for contributing! 🎉
