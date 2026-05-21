# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

**Setup (first time):**
```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

**Build the vector store (required before running the app):**
```powershell
python ingest.py
```

**Run the chat UI:**
```powershell
streamlit run src/app.py
```

**Prerequisites:** Ollama must be running locally with `llama3.2` pulled:
```powershell
ollama pull llama3.2
```

## Architecture

This is a **cybersecurity Agentic RAG** system. The key distinction from simple RAG: the LLM *decides* whether to retrieve from the vector store or answer directly, rather than always retrieving.

### Data flow

```
User question → Streamlit (app.py) → Agent (llama3.2 via Ollama)
                                          │
                              (if cybersecurity topic)
                                          ↓
                              ChromaDB retriever (search_cybersecurity_docs tool)
                              MiniLM embeddings (all-MiniLM-L6-v2, CPU)
```

### Module responsibilities

- **[ingest.py](ingest.py)** — One-shot CLI script. Orchestrates the full pipeline: fetch → chunk → embed → persist. Skips re-ingestion if `vectorstore/` already exists (prompts to overwrite).
- **[src/ingestion.py](src/ingestion.py)** — Downloads a hardcoded list of 15 Wikipedia cybersecurity topics, then chunks them (500-char chunks, 50-char overlap via `RecursiveCharacterTextSplitter`).
- **[src/vectorstore.py](src/vectorstore.py)** — Wraps ChromaDB. `create_vectorstore()` embeds and persists; `load_vectorstore()` opens existing store. Embeddings use `all-MiniLM-L6-v2` (CPU, ~80 MB). The store is saved to `vectorstore/` relative to the project root.
- **[src/agent.py](src/agent.py)** — Builds the LangChain 1.x tool-calling agent. `build_search_tool()` wraps the Chroma retriever (top-4 results) as a `@tool`. `build_agent()` combines `ChatOllama(llama3.2)` + the tool via `create_agent`. `run_agent()` invokes the agent and extracts the final text from the message list.
- **[src/app.py](src/app.py)** — Streamlit UI. The agent is cached with `@st.cache_resource` (built once per session). Chat history lives in `st.session_state`.

### Key design decisions

- The agent uses `temperature=0` for deterministic tool-calling decisions.
- `load_vectorstore()` raises `FileNotFoundError` if `vectorstore/` doesn't exist — the app will fail to start unless `ingest.py` has been run first.
- To add new knowledge base topics, edit `CYBERSECURITY_TOPICS` in [src/ingestion.py](src/ingestion.py) and re-run `ingest.py`.
