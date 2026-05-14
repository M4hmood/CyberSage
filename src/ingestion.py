"""
ingestion.py
------------
Fetches cybersecurity articles from Wikipedia, then chunks them
into smaller pieces ready to be embedded and stored.
"""

import wikipedia
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document

# The topics we want to build our knowledge base from
CYBERSECURITY_TOPICS = [
    "Cybersecurity",
    "Phishing",
    "SQL injection",
    "Zero-day vulnerability",
    "Ransomware",
    "Man-in-the-middle attack",
    "Denial-of-service attack",
    "Firewall (computing)",
    "Encryption",
    "Social engineering (security)",
    "Malware",
    "Intrusion detection system",
    "Vulnerability (computing)",
    "Computer virus",
    "Brute-force attack",
]


def fetch_wikipedia_articles(topics: list = CYBERSECURITY_TOPICS) -> list:
    """
    Downloads Wikipedia pages for each topic and returns a list of Documents.
    Each Document holds the full article text + metadata (title, URL).
    """
    docs = []
    for topic in topics:
        try:
            print(f"  Fetching: {topic}...")
            page = wikipedia.page(topic, auto_suggest=False)
            doc = Document(
                page_content=page.content,
                metadata={"source": page.url, "title": page.title}
            )
            docs.append(doc)
        except wikipedia.exceptions.DisambiguationError as e:
            # If the topic is ambiguous, try the first suggestion
            try:
                page = wikipedia.page(e.options[0], auto_suggest=False)
                doc = Document(
                    page_content=page.content,
                    metadata={"source": page.url, "title": page.title}
                )
                docs.append(doc)
            except Exception:
                print(f"  Skipping {topic} (disambiguation issue)")
        except Exception as e:
            print(f"  Skipping {topic}: {e}")

    print(f"\nFetched {len(docs)} articles successfully.")
    return docs


def chunk_documents(docs: list) -> list:
    """
    Splits long documents into smaller overlapping chunks.
    - chunk_size=500: each chunk is ~500 characters
    - chunk_overlap=50: chunks overlap by 50 chars so context isn't cut off
    """
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,
        chunk_overlap=50,
        separators=["\n\n", "\n", ". ", " "]
    )
    chunks = splitter.split_documents(docs)
    print(f"Split into {len(chunks)} chunks from {len(docs)} documents.")
    return chunks
