# Configuration

CRIS uses a simple environment-based configuration:

1. **`.env`** → Set `CRIS_ENV` to select the environment
2. **`config/models.yml`** → Defines what each environment contains

## Quick Start

### Using Gemini 3 (Default - Cloud)

```env
# .env
CRIS_ENV=gemini
GOOGLE_API_KEY=your_api_key_here
```

### Using Ollama (Local - Free)

```env
# .env
CRIS_ENV=ollama
```

```bash
# Install Ollama: https://ollama.ai
ollama pull llama3.2
ollama serve
```

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `CRIS_ENV` | Environment: `gemini` or `ollama` | `gemini` |
| `GOOGLE_API_KEY` | Required when `CRIS_ENV=gemini` | - |
| `OLLAMA_BASE_URL` | Ollama server URL | `http://localhost:11434/v1` |

## Environments

### `gemini` - Google Gemini 3 (Cloud)

- **Provider:** Google Gemini
- **Model:** `gemini-3-pro`
- **Requires:** `GOOGLE_API_KEY`

### `ollama` - Local LLM (Free)

- **Provider:** Ollama
- **Model:** `llama3.2`
- **Requires:** Ollama running locally

**Recommended Ollama models:**
```bash
ollama pull llama3.2   # General purpose
ollama pull mistral    # Fast
ollama pull qwen2.5    # Good for analysis
```

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

## Model Configuration (`config/models.yml`)

The `models.yml` file defines environments and agent-specific settings:

```yaml
environments:
  gemini:
    provider: gemini
    model: gemini-3-pro
    temperature: 0.7
    max_tokens: 8192

  ollama:
    provider: ollama
    model: llama3.2
    temperature: 0.7
    max_tokens: 4096

# Agent temperature overrides
agents:
  profiler_agent:
    temperature: 0.8  # Higher for behavioral insights
  link_agent:
    temperature: 0.5  # Lower for precise analysis
```

## Example `.env` Files

### Gemini 3 (Hackathon Default)

```env
CRIS_ENV=gemini
GOOGLE_API_KEY=your_key_here

NEO4J_URI=bolt://localhost:7687
NEO4J_PASSWORD=crispassword

DEBUG=true
```

### Ollama (Local Development)

```env
CRIS_ENV=ollama

NEO4J_URI=bolt://localhost:7687
NEO4J_PASSWORD=crispassword

DEBUG=true
```
