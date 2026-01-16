# Getting Started with CRIS

This guide will help you set up your own instance of CRIS and start your first digital investigation.

## 📋 Prerequisites

Before you begin, ensure you have the following installed:

- **Python 3.11 or higher**
- **Docker & Docker Compose**
- **[uv](https://github.com/astral-sh/uv)** (Recommended package manager)

## 🛠️ Installation

### 1. Clone the Repository

```bash
git clone https://github.com/cris-project/cris.git
cd cris
```

### 2. Set Up Environment

```bash
# Install dependencies
uv sync

# Copy environment template
cp .env.example .env
```

### 3. Configure API Keys

Open the `.env` file and add your credentials. CRIS works best with **Google Gemini**, but also supports OpenAI and Anthropic.

```env
LLM_PROVIDER=gemini
GOOGLE_API_KEY=your_gemini_api_key_here
```

### 4. Launch Infrastructure

CRIS uses Neo4j for its knowledge graph. The easiest way to run it is via Docker:

```bash
docker-compose up -d
```

### 5. Initialize the System

Run the initialization script to set up graph constraints and indexes:

```bash
uv run python -m database.init_schema
```

## 🚀 Running CRIS

Start the web dashboard using Streamlit:

```bash
uv run streamlit run app.py
```

Open your browser at `http://localhost:8501`.

## 📁 Your First Investigation

1. **Go to the "Cases" page** in the sidebar.
2. **Create a new case** by giving it a title and description.
3. **Upload evidence**: Drag and drop PDF reports, witness statements, or CCTV frames.
4. **Click "Process & Index"**: CRIS will extract entities, build the timeline, and populate the graph.
5. **Go to "Analysis"**: Start chatting with CRIS about your case. Ask questions like:
   - *"Are there any other cases with a similar MO?"*
   - *"Based on these statements, are there any inconsistencies?"*
   - *"Generate a behavioral profile for the primary suspect."*

## 🧪 Testing with Sample Data

You can load sample data into the system to explore features without uploading your own files.

```bash
# Load sample cases (coming soon in CLI)
# uv run python -m data.load_samples
```
