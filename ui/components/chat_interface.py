"""Chat Interface Component - Powered by Gemini 3 + ADK + A2A.

Provides a natural language interface for interacting with CRIS agents.
Shows real-time agent delegation and A2A communication flow.
"""

import asyncio
from typing import Optional

import streamlit as st

from agents import create_cris_system, OrchestratorAgent
from core.a2a_server import A2ARegistry


def get_orchestrator() -> OrchestratorAgent:
    """Get or create the CRIS orchestrator."""
    if "orchestrator" not in st.session_state:
        st.session_state.orchestrator = create_cris_system()
    return st.session_state.orchestrator


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


def render_a2a_flow():
    """Render the A2A communication flow visualization."""
    registry = A2ARegistry()
    agents = registry.list_agents()
    
    if not agents:
        return
    
    with st.expander("🔗 A2A Agent Network", expanded=False):
        st.markdown("### Registered Agents")
        
        cols = st.columns(min(len(agents), 3))
        for i, agent_card in enumerate(agents):
            with cols[i % 3]:
                st.markdown(
                    f"""
                    <div style="
                        padding: 12px;
                        border: 1px solid #e0e0e0;
                        border-radius: 8px;
                        margin: 4px;
                        background: white;
                    ">
                        <h4 style="margin: 0 0 8px 0; color: #1a73e8;">
                            {agent_card.name}
                        </h4>
                        <p style="font-size: 0.85em; color: #666; margin: 0;">
                            {agent_card.description[:100]}...
                        </p>
                        <div style="margin-top: 8px;">
                            <span style="
                                background: #e8f0fe;
                                color: #1a73e8;
                                padding: 2px 8px;
                                border-radius: 12px;
                                font-size: 0.75em;
                            ">
                                {len(agent_card.skills)} skills
                            </span>
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True
                )


def render_chat_interface():
    """Render the chat UI for investigative queries with A2A visualization."""
    
    # Header with Gemini 3 branding
    st.markdown(
        """
        <div style="
            display: flex;
            align-items: center;
            margin-bottom: 20px;
        ">
            <h2 style="margin: 0;">💬 Ask CRIS</h2>
            <span style="
                margin-left: 12px;
                background: linear-gradient(135deg, #4285F4, #34A853);
                color: white;
                padding: 4px 12px;
                border-radius: 16px;
                font-size: 0.75em;
                font-weight: 500;
            ">
                Powered by Gemini 3 + ADK + A2A
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
    
    # Show A2A network
    render_a2a_flow()
    
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
            
            with st.spinner("CRIS agents are collaborating..."):
                try:
                    # Get orchestrator and process query
                    orchestrator = get_orchestrator()
                    
                    # Run async query
                    loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(loop)
                    
                    try:
                        result = loop.run_until_complete(
                            orchestrator.process_query(
                                query=prompt,
                                case_id=st.session_state.get("current_case_id")
                            )
                        )
                        
                        response = result.get("response", "I couldn't process that query. Please try again.")
                        
                        # Update activities based on result
                        with activity_container:
                            render_agent_activity("orchestrator", "completed", "Query processed successfully")
                            activities.append({"agent": "orchestrator", "status": "completed", "message": "Query processed"})
                            
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
        
        # Model selection
        model = st.selectbox(
            "Gemini Model",
            ["gemini-2.0-flash", "gemini-2.0-flash-lite", "gemini-1.5-pro"],
            index=0,
            help="Select the Gemini model for agent reasoning"
        )
        
        # Agent selection
        st.markdown("#### Active Agents")
        agents = {
            "link_agent": st.checkbox("🔗 Link Agent", value=True),
            "profiler_agent": st.checkbox("🎯 Profiler Agent", value=True),
            "geo_intel_agent": st.checkbox("🗺️ Geo-Intel Agent", value=True),
            "witness_agent": st.checkbox("👁️ Witness Agent", value=True),
            "predictor_agent": st.checkbox("📊 Predictor Agent", value=True),
            "osint_agent": st.checkbox("🌐 OSINT Agent", value=True),
        }
        
        st.session_state.active_agents = [k for k, v in agents.items() if v]
        
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
