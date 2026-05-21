"""
agent.py
--------
Agentic RAG core. Supports two LLM providers:
  - "ollama"  → ChatOllama (local, no API key)
  - "groq"    → ChatGroq   (cloud, requires GROQ_API_KEY)

The agent decides whether to call search_cybersecurity_docs or answer directly.
"""

from langchain_ollama import ChatOllama
from langchain_groq import ChatGroq
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


def build_search_tool(vectorstore):
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


def build_agent(model: str = "llama3.2", provider: str = "ollama", groq_api_key: str | None = None):
    """
    Builds the tool-calling agent.
    provider: "ollama" or "groq"
    groq_api_key: required when provider="groq" (falls back to GROQ_API_KEY env var if None)
    """
    print("Loading vector store...")
    vectorstore = load_vectorstore()

    print(f"Loading {provider} / {model}...")
    if provider == "groq":
        kwargs = {"model": model, "temperature": 0}
        if groq_api_key:
            kwargs["api_key"] = groq_api_key
        llm = ChatGroq(**kwargs)
    else:
        llm = ChatOllama(model=model, temperature=0)

    tools = [build_search_tool(vectorstore)]
    agent = create_agent(model=llm, tools=tools, system_prompt=SYSTEM_PROMPT)
    print("Agent ready.")
    return agent


def run_agent(agent, user_input: str) -> str:
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
