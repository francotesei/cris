# Configuration Reference

CRIS is configured primarily through environment variables. You can set these in a `.env` file in the project root.

## 🤖 LLM Configuration

| Variable | Description | Default |
|----------|-------------|---------|
| `LLM_PROVIDER` | Provider to use (`gemini`, `openai`, `anthropic`) | `gemini` |
| `GOOGLE_API_KEY` | API Key for Google Gemini | - |
| `OPENAI_API_KEY` | API Key for OpenAI | - |
| `ANTHROPIC_API_KEY` | API Key for Anthropic Claude | - |
| `LLM_MODEL` | Specific model ID to use | `gemini-1.5-pro` |
| `LLM_TEMPERATURE` | Generation temperature (0-1) | `0.7` |
| `LLM_MAX_TOKENS` | Max tokens per response | `4096` |

## 🗄️ Database Configuration

### Neo4j (Graph)
| Variable | Description | Default |
|----------|-------------|---------|
| `NEO4J_URI` | Bolt/Neo4j connection URI | `bolt://localhost:7687` |
| `NEO4J_USER` | Username | `neo4j` |
| `NEO4J_PASSWORD` | Password | `crispassword` |

### ChromaDB (Vectors)
| Variable | Description | Default |
|----------|-------------|---------|
| `CHROMA_PERSIST_DIR` | Path to store vector database | `./data/chroma` |
| `EMBEDDING_MODEL` | Sentence-transformers model for vectors | `all-MiniLM-L6-v2` |

## 🔌 Plugin Configuration

| Variable | Description | Default |
|----------|-------------|---------|
| `PLUGINS_DIR` | Directory to look for plugins | `./plugins` |
| `ENABLED_PLUGINS` | Comma-separated list of plugins to load | (all) |

## 📍 Geospatial Configuration

| Variable | Description | Default |
|----------|-------------|---------|
| `GEOCODING_PROVIDER` | Provider for address resolution (`nominatim`, `google`) | `nominatim` |
| `GOOGLE_MAPS_API_KEY` | Required if using Google geocoder | - |

## ⚙️ Feature Flags

| Variable | Description | Default |
|----------|-------------|---------|
| `DEBUG` | Enable debug logging and UI features | `true` |
| `ENABLE_OSINT` | Enable the (experimental) OSINT agent | `false` |
| `ENABLE_PREDICTIONS` | Show predictive analytics in UI | `true` |
| `LOG_LEVEL` | Minimum log level (`DEBUG`, `INFO`, `WARN`, `ERROR`) | `INFO` |

## 🛡️ Security

| Variable | Description | Default |
|----------|-------------|---------|
| `SECRET_KEY` | Random string for session protection | - |
| `SESSION_TIMEOUT` | Seconds before session expires | `3600` |
