"""Chat Interface Component.

Provides a natural language interface for interacting with CRIS agents.
"""

import streamlit as st

def render_chat_interface():
    """Render the chat UI for investigative queries."""
    
    st.subheader("💬 Ask CRIS")
    st.caption("Query the knowledge graph, ask for profiles, or simulate scenarios.")

    # Initialize chat history
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # Display chat messages from history
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # React to user input
    if prompt := st.chat_input("Analyze witness Sarah L's statement for inconsistencies..."):
        # Display user message in chat message container
        with st.chat_message("user"):
            st.markdown(prompt)
        # Add user message to chat history
        st.session_state.messages.append({"role": "user", "content": prompt})

        # Display assistant response in chat message container
        with st.chat_message("assistant"):
            with st.spinner("CRIS is thinking..."):
                # In real app, call OrchestratorAgent here
                response = "I've analyzed the request. Finding connections to related cases..."
                st.markdown(response)
        # Add assistant response to chat history
        st.session_state.messages.append({"role": "assistant", "content": response})
