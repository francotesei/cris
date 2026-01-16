# CRIS - Criminal Reasoning Intelligence System

[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Gemini 3](https://img.shields.io/badge/Powered%20by-Gemini%203-4285F4.svg)](https://deepmind.google/technologies/gemini/)

> Multi-agent AI platform for criminal intelligence powered by **Gemini 3 + ADK + A2A**

**Built for the Google DeepMind Gemini 3 Hackathon** 🚀

## Overview

CRIS (Criminal Reasoning Intelligence System) is a multi-agent AI platform for criminal intelligence, investigation, and predictive analysis. It helps law enforcement agencies solve crimes faster by connecting evidence, profiling suspects, and predicting criminal behavior patterns.

**Core Value Proposition:** Not just process what happened (reactive), but anticipate what could happen (proactive).

## ✨ Key Capabilities

### 🔗 Evidence & Case Linking
- **Knowledge graphs** that reveal hidden relationships between cases, people, and evidence
- **Serial pattern detection** by analyzing similar MO (modus operandi)
- **Common suspect identification** across multiple cases
- **Criminal network analysis** through community detection

### 🎯 Criminal Profiling
- **FBI BAU-style behavioral analysis** to generate psychological profiles
- **Risk level assessment** for known suspects
- **Recidivism prediction** based on history and profile
- **Victimology analysis** to understand selection patterns

### 🗺️ Geospatial Intelligence
- **Crime hotspot maps** using kernel density estimation
- **Geographic profiling** using Rossmo's formula
- **Next location prediction** for suspects
- **Temporal patterns** (time of day, day of week, seasonality)

### 👁️ Witness Statement Analysis
- **Automatic key fact extraction** from narrative statements
- **Inconsistency detection** internal and cross-referenced
- **Credibility assessment** based on linguistic indicators
- **Deception indicator identification**
- **Follow-up question generation**

### 🔮 Predictions & Simulations
- **Monte Carlo simulation** of suspect behavior
- **Escalation prediction** to more serious crimes
- **"What-if" scenario modeling**
- **Crime trend forecasting**

### 🌐 Open Source Intelligence (OSINT)
- **Digital footprint analysis** on social media
- **Online threat assessment**
- **Digital contact network mapping**

## Architecture

```mermaid
flowchart TB
    subgraph UI["🖥️ Streamlit UI"]
        User([User Query])
    end
    
    subgraph Orchestration["🧠 Orchestration Layer"]
        Orch[Orchestrator Agent<br/>Gemini 3 + ADK]
    end
    
    subgraph A2A["📡 A2A Protocol"]
        Protocol{A2A<br/>Delegation}
    end
    
    subgraph Agents["🤖 Specialized Agents"]
        Link[Link Agent]
        Profiler[Profiler Agent]
        GeoIntel[Geo-Intel Agent]
        Witness[Witness Agent]
        Predictor[Predictor Agent]
        OSINT[OSINT Agent]
    end
    
    subgraph Data["💾 Data Layer"]
        Neo4j[(Neo4j)]
        Chroma[(ChromaDB)]
    end
    
    User --> Orch
    Orch --> Protocol
    Protocol --> Link & Profiler & GeoIntel & Witness & Predictor & OSINT
    Link & Profiler & GeoIntel & Witness & Predictor & OSINT --> Neo4j & Chroma
```

## Tech Stack

| Component | Technology |
|-----------|------------|
| **AI Engine** | Gemini 3 (`gemini-2.0-flash`) |
| **Agent Framework** | Google ADK |
| **Agent Communication** | A2A Protocol |
| **Knowledge Graph** | Neo4j |
| **Vector Search** | ChromaDB |
| **Frontend** | Streamlit |

## Quick Start

```bash
# Clone and install
git clone https://github.com/cris-project/cris.git
cd cris
uv sync

# Configure
cp .env.example .env
# Add GOOGLE_API_KEY to .env

# Start Neo4j
docker-compose up -d

# Run
uv run streamlit run app.py
```

## Agents

| Agent | Purpose | Key Tools |
|-------|---------|-----------|
| **Orchestrator** | Central coordinator | `delegate_to_agent`, `synthesize_results` |
| **Link Agent** | Graph analysis | `find_similar_cases`, `detect_serial_patterns` |
| **Profiler Agent** | Behavioral profiling | `generate_full_profile`, `assess_risk_level` |
| **Geo-Intel Agent** | Spatial analysis | `generate_hotspot_map`, `predict_next_location` |
| **Witness Agent** | Statement analysis | `analyze_statement`, `detect_inconsistencies` |
| **Predictor Agent** | Forecasting | `predict_next_action`, `model_scenarios` |
| **OSINT Agent** | Digital intelligence | `analyze_digital_footprint`, `assess_online_threat` |

## 📊 Usage Examples

### Natural Language Queries
CRIS understands natural language queries like:

- *"Are there similar cases to this robbery in the south district?"*
- *"Generate a suspect profile based on the crime scene"*
- *"Where is the next incident most likely to occur?"*
- *"Analyze inconsistencies between witness statements"*
- *"What connections does this suspect have with other cases?"*

### Typical Workflow

1. **Case Upload** → Upload documents, photos, statements
2. **Automatic Extraction** → Entities, locations, timeline
3. **Multi-Agent Analysis** → Each agent processes its specialty
4. **Result Synthesis** → Orchestrator combines insights
5. **Visualization** → Graphs, maps, profiles, predictions

## 🔒 Ethical Considerations

CRIS is designed as a **support tool** for investigators, not a replacement for human judgment:

- All predictions include **confidence levels**
- Profiles are **hypotheses to verify**, not conclusions
- The system maintains **traceability** of all decisions
- Designed to **reduce bias**, not amplify it

## Documentation

- [Architecture](docs/architecture.md) - Full technical details
- [Getting Started](docs/getting-started.md) - Setup guide
- [Creating Agents](docs/agents/creating-agents.md) - Extend CRIS

## License

MIT License - See [LICENSE](LICENSE)

---

**Built with ❤️ for justice**
