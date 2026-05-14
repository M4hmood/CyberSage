"""
agent.py
--------
The heart of the Agentic RAG system.

This is what makes it "agentic" vs a simple RAG:
  - A simple RAG ALWAYS searches the vector DB, no matter what
  - An agent DECIDES whether to search or answer directly

The agent uses tool-calling: the LLM (llama3.2) decides on its own
whether to call the search tool or answer directly, based on the question.
"""

from langchain_ollama import ChatOllama
from langchain.agents import create_agent
from langchain_core.tools import tool
from src.vectorstore import load_vectorstore


SYSTEM_PROMPT = (
    "You are a knowledgeable cybersecurity assistant. "
    "For any question about cybersecurity — attacks, malware, defenses, "
    "encryption, vulnerabilities, etc. — always use the search_cybersecurity_docs tool first. "
    "Base your answer on the search results and cite the source when possible. "
    "For greetings or off-topic questions, answer directly without searching."
)


# ── Tool definition ────────────────────────────────────────────────────────────

def build_search_tool(vectorstore):
    """Creates the search tool that queries ChromaDB."""
    retriever = vectorstore.as_retriever(search_kwargs={"k": 4})

    @tool
    def search_cybersecurity_docs(query: str) -> str:
        """
        Searches a knowledge base of cybersecurity articles from Wikipedia.
        Use this for ANY question about cybersecurity topics: attacks, defenses,
        malware, encryption, firewalls, vulnerabilities, etc.
        Input should be a clear search query.
        """
        docs = retriever.invoke(query)
        if not docs:
            return "No relevant documents found for this query."

        results = []
        for doc in docs:
            title = doc.metadata.get("title", "Unknown")
            results.append(f"[Source: {title}]\n{doc.page_content}")

        return "\n\n---\n\n".join(results)

    return search_cybersecurity_docs


# ── Agent builder ──────────────────────────────────────────────────────────────

def build_agent():
    """
    Builds and returns the LangChain tool-calling agent (LangChain 1.x).
    Call this once at startup and reuse the returned agent.
    """
    print("Loading vector store...")
    vectorstore = load_vectorstore()

    print("Loading Ollama (llama3.2)...")
    llm = ChatOllama(model="llama3.2", temperature=0)

    tools = [build_search_tool(vectorstore)]

    agent = create_agent(
        model=llm,
        tools=tools,
        system_prompt=SYSTEM_PROMPT,
    )

    print("Agent ready.")
    return agent


def run_agent(agent, user_input: str) -> str:
    """
    Invoke the agent with a single user message and return the final text reply.
    """
    result = agent.invoke({"messages": [{"role": "user", "content": user_input}]})
    messages = result.get("messages", [])
    if not messages:
        return ""
    final = messages[-1]
    content = getattr(final, "content", final)
    if isinstance(content, list):
        parts = []
        for part in content:
            if isinstance(part, dict) and "text" in part:
                parts.append(part["text"])
            else:
                parts.append(str(part))
        return "".join(parts)
    return str(content)
