# Configuration

CRIS is configured via environment variables in `.env`.

## Gemini 3 / ADK

| Variable | Description | Default |
|----------|-------------|---------|
| `GOOGLE_API_KEY` | Gemini API key | Required |
| `GEMINI_MODEL` | Model to use | `gemini-2.0-flash` |
| `GEMINI_TEMPERATURE` | Generation temperature | `0.7` |
| `GEMINI_MAX_TOKENS` | Max tokens per response | `8192` |

## A2A Protocol

| Variable | Description | Default |
|----------|-------------|---------|
| `A2A_ENABLE` | Enable A2A communication | `true` |
| `A2A_SERVER_PORT` | A2A server port | `8080` |
| `A2A_ENABLE_STREAMING` | Enable streaming responses | `true` |

## Database

### Neo4j
| Variable | Description | Default |
|----------|-------------|---------|
| `NEO4J_URI` | Connection URI | `bolt://localhost:7687` |
| `NEO4J_USER` | Username | `neo4j` |
| `NEO4J_PASSWORD` | Password | `crispassword` |

### ChromaDB
| Variable | Description | Default |
|----------|-------------|---------|
| `CHROMA_PERSIST_DIR` | Vector store path | `./data/chroma` |
| `EMBEDDING_MODEL` | Embedding model | `all-MiniLM-L6-v2` |

## Feature Flags

| Variable | Description | Default |
|----------|-------------|---------|
| `DEBUG` | Enable debug mode | `true` |
| `ENABLE_PREDICTIONS` | Enable predictor agent | `true` |
| `ENABLE_OSINT` | Enable OSINT agent | `false` |
| `LOG_LEVEL` | Log level | `INFO` |

## Example `.env`

```env
# Required
GOOGLE_API_KEY=your_key_here

# Gemini 3
GEMINI_MODEL=gemini-2.0-flash
GEMINI_TEMPERATURE=0.7

# Database
NEO4J_URI=bolt://localhost:7687
NEO4J_PASSWORD=crispassword

# Features
DEBUG=true
ENABLE_PREDICTIONS=true
```
