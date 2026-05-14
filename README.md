# Cybersecurity RAG Agent

An **agentic** Retrieval-Augmented Generation system that answers cybersecurity questions using a local LLM (`llama3.2` via Ollama) grounded in a knowledge base of Wikipedia articles. The agent decides on its own whether to search the vector store or answer directly.

## How it works

1. **Ingestion** — Wikipedia articles on cybersecurity topics are downloaded, split into ~500-character overlapping chunks, embedded with `all-MiniLM-L6-v2`, and persisted to ChromaDB.
2. **Agent** — A LangChain 1.x tool-calling agent wraps `ChatOllama(llama3.2)` with a single tool, `search_cybersecurity_docs`, that queries ChromaDB. The system prompt tells the LLM to call the tool for cybersecurity questions and answer directly for greetings / off-topic input.
3. **UI** — A Streamlit chat interface invokes the agent and renders the conversation.

```
User question
     │
     ▼
┌─────────────────────────┐      ┌──────────────────────┐
│  Streamlit chat (app.py)│ ───► │  Agent (llama3.2)    │
└─────────────────────────┘      │  decides: tool call? │
                                 └──────┬───────────────┘
                                        │ (if yes)
                                        ▼
                                 ┌──────────────────────┐
                                 │ ChromaDB retriever   │
                                 │ (MiniLM embeddings)  │
                                 └──────────────────────┘
```

## Files

| Path | Purpose |
|---|---|
| `ingest.py` | One-shot script run before first use. Fetches Wikipedia pages, chunks them, embeds them, and writes ChromaDB to `vectorstore/`. Skips re-ingestion if the store already exists. |
| `src/ingestion.py` | `fetch_wikipedia_articles()` downloads pages for a fixed list of topics; `chunk_documents()` splits with `RecursiveCharacterTextSplitter` (size 500, overlap 50). |
| `src/vectorstore.py` | `get_embeddings()` returns the HuggingFace MiniLM model; `create_vectorstore()` persists a new Chroma store; `load_vectorstore()` opens the existing one. |
| `src/agent.py` | `build_search_tool()` wraps the retriever as a LangChain `@tool`; `build_agent()` constructs the agent via `langchain.agents.create_agent` (LangChain 1.x API); `run_agent()` invokes it and extracts the final text reply. |
| `src/app.py` | Streamlit UI. Caches the agent with `@st.cache_resource`, renders chat history in `st.session_state`, and routes each prompt through `run_agent()`. |
| `requirements.txt` | Pinned dependency ranges (LangChain 1.x, langchain-chroma, langchain-huggingface, langchain-ollama, streamlit, chromadb, sentence-transformers, wikipedia). |
| `vectorstore/` | ChromaDB persistence directory (created by `ingest.py`). |
| `documents/` | Reserved for any local source documents you might add later. |

## Setup

### Prerequisites

- **Python 3.11+**
- **[Ollama](https://ollama.com/)** installed and running locally
- The `llama3.2` model pulled:
  ```
  ollama pull llama3.2
  ```
  Verify Ollama is up: `curl http://localhost:11434/api/tags` should list the model.

### Install dependencies

From the project root (PowerShell):

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

## Run

### 1. Build the vector store (one time)

```powershell
python ingest.py
```

This downloads ~15 Wikipedia articles, chunks them, and writes ChromaDB to `vectorstore/`. Re-running prompts before overwriting an existing store.

### 2. Launch the chat UI

```powershell
streamlit run src/app.py
```

Open http://localhost:8501 and ask questions like:
- *"What is phishing?"* → the agent calls the search tool and answers with citations.
- *"hello"* → the agent answers directly without searching.

## Tech stack

- **LangChain 1.x** — agent framework (`create_agent`)
- **Ollama + llama3.2** — local LLM (no API keys needed)
- **ChromaDB** — local persistent vector store
- **HuggingFace `all-MiniLM-L6-v2`** — CPU-friendly embeddings (~80 MB)
- **Streamlit** — chat UI
