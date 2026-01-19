# Changelog

## [0.2.0] - 2026-01-16

### 🚀 Major Refactor: Gemini 3 + ADK + A2A

Complete architecture overhaul for the Google DeepMind Gemini 3 Hackathon.

### Added
- **Google ADK Integration**: All agents now use `CRISADKAgent` base class
- **A2A Protocol**: Inter-agent communication via Agent-to-Agent protocol
- **Gemini 3 Support**: Using `gemini-3-pro` as reasoning engine
- **Ollama Support**: Run locally with `llama3.2`, `qwen2.5`, `mistral` - no API costs!
- **Agent Cards**: A2A capability advertisement for agent discovery
- **New Tools**: 40+ specialized tools across all agents
- **Streaming Support**: Real-time response streaming via A2A

### Changed
- Migrated all 7 agents to ADK architecture
- Updated configuration for Gemini 3 and A2A settings
- Redesigned chat interface with agent activity visualization
- Consolidated documentation

### Technical Details
- `core/adk_agent.py`: New ADK base classes
- `core/a2a_server.py`: A2A protocol implementation
- All agents in `agents/` refactored with tools

---

## [0.1.0] - 2024-01-15

### Added
- Initial project structure
- Multi-agent architecture design
- Neo4j and ChromaDB integration
- Pluggable agent system
- Basic Streamlit UI
- Documentation foundation
