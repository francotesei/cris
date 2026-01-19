"""Chat Interface Component - Gemini 3 + ADK + A2A.

Provides a natural language interface for interacting with CRIS agents.
Shows real-time agent delegation and communication flow.

Built for the Google Gemini 3 Hackathon 🚀
Default: Gemini 3 Pro | Alternative: Ollama (local)

Configuration via: .env or config/models.yml
"""

import asyncio
from typing import Optional

import streamlit as st

from config.settings import get_settings
from services.llm_service import LLMService
from config.prompts import ORCHESTRATOR_SYSTEM_PROMPT


def get_llm_service() -> LLMService:
    """Get or create the LLM service based on configured provider."""
    if "llm_service" not in st.session_state:
        st.session_state.llm_service = LLMService()
    return st.session_state.llm_service


def is_using_ollama() -> bool:
    """Check if we're using Ollama as the LLM environment."""
    settings = get_settings()
    return settings.cris_env == "ollama"


async def process_with_llm(query: str, case_context: Optional[str] = None) -> str:
    """Process a query using the configured LLM service.
    
    This is a simplified version that works with any LLM provider,
    including Ollama for local inference.
    """
    llm = get_llm_service()
    
    # Build context-aware prompt
    context_info = f"\n\nCurrent Case Context: {case_context}" if case_context else ""
    
    prompt = f"""You are CRIS (Criminal Reasoning Intelligence System), an AI assistant 
specialized in criminal investigation analysis.

{ORCHESTRATOR_SYSTEM_PROMPT}
{context_info}

User Query: {query}

Provide a detailed, professional response that would help an investigator. 
Include relevant analysis, potential connections, and recommended next steps."""

    response = await llm.generate(prompt)
    return response


def render_agent_activity(agent_name: str, status: str, message: str = ""):
    """Render an agent activity indicator."""
    status_icons = {
        "working": "🔄",
        "completed": "✅",
        "delegating": "📤",
        "receiving": "📥",
        "error": "❌",
    }
    icon = status_icons.get(status, "⚪")
    
    agent_colors = {
        "orchestrator": "#4285F4",  # Google Blue
        "link_agent": "#EA4335",     # Google Red
        "profiler_agent": "#FBBC04", # Google Yellow
        "geo_intel_agent": "#34A853", # Google Green
        "witness_agent": "#9C27B0",   # Purple
        "predictor_agent": "#FF5722", # Deep Orange
        "osint_agent": "#00BCD4",     # Cyan
    }
    color = agent_colors.get(agent_name, "#757575")
    
    st.markdown(
        f"""
        <div style="
            display: flex;
            align-items: center;
            padding: 8px 12px;
            margin: 4px 0;
            background: linear-gradient(135deg, {color}15, {color}05);
            border-left: 3px solid {color};
            border-radius: 4px;
            font-size: 0.9em;
        ">
            <span style="margin-right: 8px;">{icon}</span>
            <strong style="color: {color};">{agent_name}</strong>
            <span style="margin-left: 8px; color: #666;">{message}</span>
        </div>
        """,
        unsafe_allow_html=True
    )


def render_provider_badge():
    """Render a compact badge showing current LLM environment."""
    from config.model_config import get_current_environment
    
    settings = get_settings()
    env_config = get_current_environment()
    
    env_name = settings.cris_env
    provider = env_config.get("provider", "gemini")
    model = env_config.get("model", "gemini-3-pro")
    
    # Provider info
    provider_info = {
        "ollama": ("🦙", "#7C3AED", "Local"),
        "gemini": ("✨", "#4285F4", "Cloud"),
        "openai": ("🤖", "#10A37F", "Cloud"),
        "anthropic": ("🧠", "#D97706", "Cloud"),
    }
    
    icon, color, mode = provider_info.get(provider, ("⚡", "#666", "Unknown"))
    
    st.markdown(
        f"""
        <div style="
            display: inline-flex;
            align-items: center;
            padding: 6px 12px;
            background: linear-gradient(135deg, {color}15, {color}05);
            border: 1px solid {color}30;
            border-radius: 8px;
            font-size: 0.85em;
            margin-bottom: 16px;
        ">
            <span style="margin-right: 6px;">{icon}</span>
            <strong style="color: {color};">{env_name.upper()}</strong>
            <span style="margin: 0 6px; color: #999;">•</span>
            <code style="font-size: 0.9em;">{model}</code>
            <span style="
                margin-left: 8px;
                background: {color}20;
                color: {color};
                padding: 2px 6px;
                border-radius: 10px;
                font-size: 0.7em;
            ">{mode}</span>
        </div>
        """,
        unsafe_allow_html=True
    )


def render_chat_interface():
    """Render the chat UI for investigative queries with A2A visualization."""
    from config.model_config import get_current_environment
    
    # Header with environment info
    settings = get_settings()
    env_config = get_current_environment()
    
    env_name = settings.cris_env
    provider = env_config.get("provider", "gemini")
    
    provider_colors = {
        "ollama": "#7C3AED",
        "gemini": "#4285F4",
        "openai": "#10A37F",
        "anthropic": "#D97706",
    }
    color = provider_colors.get(provider, "#666")
    
    st.markdown(
        f"""
        <div style="
            display: flex;
            align-items: center;
            margin-bottom: 20px;
        ">
            <h2 style="margin: 0;">💬 Ask CRIS</h2>
            <span style="
                margin-left: 12px;
                background: linear-gradient(135deg, {color}, {color}CC);
                color: white;
                padding: 4px 12px;
                border-radius: 16px;
                font-size: 0.75em;
                font-weight: 500;
            ">
                {env_name.upper()} • Multi-Agent AI
            </span>
        </div>
        """,
        unsafe_allow_html=True
    )
    
    st.caption(
        "Query the knowledge graph, ask for profiles, analyze statements, "
        "or run predictive simulations. CRIS will automatically route your "
        "query to the appropriate specialized agents."
    )
    
    # Show provider badge (compact, read-only)
    render_provider_badge()
    
    # Initialize chat history
    if "messages" not in st.session_state:
        st.session_state.messages = []
    
    if "agent_activities" not in st.session_state:
        st.session_state.agent_activities = []

    # Display chat messages from history
    for message in st.session_state.messages:
        with st.chat_message(message["role"], avatar="🔍" if message["role"] == "assistant" else None):
            st.markdown(message["content"])
            
            # Show agent activities for this message
            if message["role"] == "assistant" and "activities" in message:
                with st.expander("🤖 Agent Activity", expanded=False):
                    for activity in message["activities"]:
                        render_agent_activity(
                            activity["agent"],
                            activity["status"],
                            activity.get("message", "")
                        )

    # Example queries
    if not st.session_state.messages:
        st.markdown("### 💡 Example Queries")
        example_cols = st.columns(2)
        
        examples = [
            ("🔗 Link Analysis", "Find all cases similar to CASE-2024-001 and identify common suspects"),
            ("🎯 Profiling", "Generate a behavioral profile for the suspect in the downtown robbery series"),
            ("🗺️ Geo-Intel", "Show crime hotspots in the metro area for the last 90 days"),
            ("👁️ Witness Analysis", "Analyze the witness statements for inconsistencies in case CASE-2024-002"),
            ("📊 Prediction", "What is the escalation risk for suspect John Doe based on his history?"),
            ("🌐 OSINT", "Analyze the digital footprint for the person of interest"),
        ]
        
        for i, (title, query) in enumerate(examples):
            with example_cols[i % 2]:
                if st.button(title, key=f"example_{i}", use_container_width=True):
                    st.session_state.pending_query = query
                    st.rerun()

    # Handle pending query from example buttons
    pending_query = st.session_state.pop("pending_query", None)
    
    # React to user input
    prompt = st.chat_input("Ask CRIS anything about your investigation...")
    
    if pending_query:
        prompt = pending_query
    
    if prompt:
        # Display user message
        with st.chat_message("user"):
            st.markdown(prompt)
        st.session_state.messages.append({"role": "user", "content": prompt})

        # Display assistant response with agent activity
        with st.chat_message("assistant", avatar="🔍"):
            # Show agent activity panel
            activity_container = st.container()
            response_container = st.container()
            
            with activity_container:
                st.markdown("**🤖 Agent Orchestration**")
                activities = []
                
                # Simulate orchestrator analysis
                render_agent_activity("orchestrator", "working", "Analyzing query intent...")
                activities.append({"agent": "orchestrator", "status": "working", "message": "Analyzing query intent..."})
            
            with st.spinner("CRIS is analyzing your query..."):
                try:
                    # Run async query using LLM service (works with Ollama and Gemini)
                    loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(loop)
                    
                    try:
                        from config.model_config import get_current_environment
                        settings = get_settings()
                        env_config = get_current_environment()
                        env_name = settings.cris_env
                        model_name = env_config.get("model", "unknown")
                        
                        response = loop.run_until_complete(
                            process_with_llm(
                                query=prompt,
                                case_context=st.session_state.get("current_case_id")
                            )
                        )
                        
                        # Update activities based on result
                        with activity_container:
                            render_agent_activity("orchestrator", "completed", f"Processed with {env_name}/{model_name}")
                            activities.append({"agent": "orchestrator", "status": "completed", "message": f"Using {env_name}"})
                            
                    except Exception as e:
                        response = f"I encountered an error processing your query: {str(e)}\n\nPlease ensure all services are running and try again."
                        
                        with activity_container:
                            render_agent_activity("orchestrator", "error", str(e)[:50])
                            activities.append({"agent": "orchestrator", "status": "error", "message": str(e)[:50]})
                    
                    finally:
                        loop.close()
                        
                except Exception as e:
                    response = f"System initialization error: {str(e)}\n\nPlease check your configuration."
                    activities.append({"agent": "orchestrator", "status": "error", "message": "Initialization failed"})
            
            with response_container:
                st.markdown("---")
                st.markdown(response)
        
        # Add to history with activities
        st.session_state.messages.append({
            "role": "assistant",
            "content": response,
            "activities": activities
        })


def render_chat_sidebar():
    """Render chat-related sidebar options."""
    with st.sidebar:
        st.markdown("### 🎛️ Chat Settings")
        
        from config.model_config import get_current_environment
        
        settings = get_settings()
        env_config = get_current_environment()
        
        env_name = settings.cris_env
        provider = env_config.get("provider", "gemini")
        model = env_config.get("model", "gemini-3-pro")
        
        provider_icons = {"gemini": "✨", "ollama": "🦙", "openai": "🤖", "anthropic": "🧠"}
        icon = provider_icons.get(provider, "⚡")
        
        st.markdown(f"""
        **{icon} Environment: `{env_name}`**  
        Model: `{model}`
        """)
        st.caption("📝 Set `CRIS_ENV` in `.env`")
        
        st.divider()
        
        # Agent selection
        st.markdown("#### 🤖 Active Agents")
        agents = {
            "link_agent": st.checkbox("🔗 Link Agent", value=True),
            "profiler_agent": st.checkbox("🎯 Profiler Agent", value=True),
            "geo_intel_agent": st.checkbox("🗺️ Geo-Intel Agent", value=True),
            "witness_agent": st.checkbox("👁️ Witness Agent", value=True),
            "predictor_agent": st.checkbox("📊 Predictor Agent", value=True),
            "osint_agent": st.checkbox("🌐 OSINT Agent", value=True),
        }
        
        st.session_state.active_agents = [k for k, v in agents.items() if v]
        
        st.divider()
        
        # Clear chat
        if st.button("🗑️ Clear Chat History", use_container_width=True):
            st.session_state.messages = []
            st.session_state.agent_activities = []
            st.rerun()
        
        # Export chat
        if st.session_state.get("messages"):
            if st.button("📥 Export Chat", use_container_width=True):
                chat_export = "\n\n".join([
                    f"**{m['role'].upper()}**: {m['content']}"
                    for m in st.session_state.messages
                ])
                st.download_button(
                    "Download",
                    chat_export,
                    file_name="cris_chat_export.md",
                    mime="text/markdown"
                )
