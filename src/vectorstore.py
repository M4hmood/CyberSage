"""
vectorstore.py
--------------
Handles creating and loading the ChromaDB vector store.

How it works:
  1. We take document chunks (text)
  2. We convert each chunk into an embedding (a list of numbers that
     captures the meaning of the text) using a free HuggingFace model
  3. We store those embeddings in ChromaDB (a local vector database)
  4. Later, when a user asks a question, we embed the question the same
     way and find the closest chunks by comparing vectors
"""

import os
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma

# Directory where ChromaDB will save its data on disk
VECTORSTORE_DIR = "vectorstore"

# Free, lightweight embedding model (~80MB) — runs on CPU
EMBEDDING_MODEL = "all-MiniLM-L6-v2"


def get_embeddings() -> HuggingFaceEmbeddings:
    """Returns the embedding model used to convert text → vectors."""
    return HuggingFaceEmbeddings(
        model_name=EMBEDDING_MODEL,
        model_kwargs={"device": "cpu"},
        encode_kwargs={"normalize_embeddings": True}
    )


def create_vectorstore(chunks: list) -> Chroma:
    """
    Takes a list of document chunks, embeds them, and stores in ChromaDB.
    This only needs to be run once (or when you update your documents).
    """
    print("Creating embeddings and storing in ChromaDB...")
    embeddings = get_embeddings()
    vectorstore = Chroma.from_documents(
        documents=chunks,
        embedding=embeddings,
        persist_directory=VECTORSTORE_DIR
    )
    print(f"Vector store created with {len(chunks)} chunks at '{VECTORSTORE_DIR}/'")
    return vectorstore


def load_vectorstore() -> Chroma:
    """
    Loads an existing ChromaDB vector store from disk.
    Call this after you've already run the ingestion script once.
    """
    if not os.path.exists(VECTORSTORE_DIR):
        raise FileNotFoundError(
            "Vector store not found. Please run 'python ingest.py' first."
        )
    embeddings = get_embeddings()
    vectorstore = Chroma(
        persist_directory=VECTORSTORE_DIR,
        embedding_function=embeddings
    )
    return vectorstore
