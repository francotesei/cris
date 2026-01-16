# Getting Started

## Prerequisites

- Python 3.11+
- Docker (for Neo4j)
- [uv](https://github.com/astral-sh/uv) package manager
- Google API Key (for Gemini 3)

## Installation

```bash
# Clone repository
git clone https://github.com/cris-project/cris.git
cd cris

# Install dependencies
uv sync

# Configure environment
cp .env.example .env
```

Edit `.env` and add your API key:

```env
GOOGLE_API_KEY=your_gemini_api_key_here
```

## Start Infrastructure

```bash
# Launch Neo4j
docker-compose up -d

# Initialize database
uv run python -m database.init_schema
```

## Run CRIS

```bash
# Web interface
uv run streamlit run app.py

# Or test agents via CLI
python main.py test-agents
python main.py query "Find similar cases to CASE-2024-001"
```

Open `http://localhost:8501`

## First Investigation

1. Go to **Cases** → Create new case
2. Upload evidence (PDFs, images)
3. Click **Process & Index**
4. Go to **Analysis** → Ask questions:
   - *"Are there similar cases?"*
   - *"Generate a behavioral profile"*
   - *"Analyze witness statements"*

## Verify Setup

```bash
python main.py test-agents
```

Expected output:
```
🧪 Testing CRIS Agents...
  ✓ Orchestrator initialized
    Model: gemini-2.0-flash
  ✓ Health check passed
  📡 A2A Registry: 6 agents registered
✅ Agent test complete!
```
