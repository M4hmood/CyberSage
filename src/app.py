"""
app.py
------
Streamlit chat interface for the Cybersecurity RAG Agent.

Run with:
    streamlit run src/app.py
"""

import sys
import os

# Add the project root to Python's path so "src" is always findable
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import streamlit as st
from src.agent import build_agent, run_agent

# ── Page config ────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="CyberSec RAG Agent",
    page_icon="🛡️",
    layout="wide"
)

# ── Header ─────────────────────────────────────────────────────────────────────
st.title("🛡️ Cybersecurity RAG Agent")
st.markdown(
    "Ask me anything about cybersecurity. "
    "I search my knowledge base of Wikipedia articles to give accurate, sourced answers."
)
st.divider()

# ── Load agent (cached so it only loads once) ──────────────────────────────────
@st.cache_resource(show_spinner="Loading agent and vector store...")
def get_agent():
    return build_agent()

agent = get_agent()

# ── Chat history ───────────────────────────────────────────────────────────────
if "messages" not in st.session_state:
    st.session_state.messages = [
        {
            "role": "assistant",
            "content": (
                "Hello! I'm your cybersecurity assistant. "
                "Ask me about threats, attacks, defenses, encryption, malware, and more!"
            )
        }
    ]

# Display previous messages
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# ── Chat input ─────────────────────────────────────────────────────────────────
if prompt := st.chat_input("Ask a cybersecurity question..."):

    # Show user message
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Get agent response
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            try:
                response = run_agent(agent, prompt)
            except Exception as e:
                response = f"⚠️ An error occurred: {str(e)}"
        st.markdown(response)

    st.session_state.messages.append({"role": "assistant", "content": response})

# ── Sidebar ────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.header("ℹ️ About this system")
    st.markdown("""
    **Architecture: Agentic RAG**

    This system uses a **ReAct agent** that:
    1. Reads your question
    2. Decides if it needs to search the knowledge base
    3. Searches ChromaDB for relevant chunks
    4. Generates a grounded answer using **llama3.2** via Ollama

    **Knowledge base topics:**
    - Phishing, Ransomware, Malware
    - SQL Injection, Brute-force attacks
    - Firewalls, Encryption, IDS
    - Zero-day vulnerabilities
    - Social engineering
    - ...and more!

    **Tech stack:**
    - 🦜 LangChain (agent framework)
    - 🦙 Ollama + llama3.2 (local LLM)
    - 🗄️ ChromaDB (vector store)
    - 🤗 HuggingFace embeddings
    """)

    st.divider()
    if st.button("🗑️ Clear chat"):
        st.session_state.messages = []
        st.rerun()
