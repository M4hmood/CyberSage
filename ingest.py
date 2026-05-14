"""
ingest.py
---------
Run this script ONCE before starting the app.
It will:
  1. Download cybersecurity articles from Wikipedia
  2. Split them into chunks
  3. Embed them and store in ChromaDB

Usage:
    python ingest.py
"""

import os
from src.ingestion import fetch_wikipedia_articles, chunk_documents
from src.vectorstore import create_vectorstore, VECTORSTORE_DIR


def main():
    # Check if vector store already exists
    if os.path.exists(VECTORSTORE_DIR) and os.listdir(VECTORSTORE_DIR):
        print(f"Vector store already exists at '{VECTORSTORE_DIR}/'.")
        answer = input("Re-ingest and overwrite? (y/n): ").strip().lower()
        if answer != "y":
            print("Skipping ingestion. Vector store is ready to use.")
            return

    print("=" * 50)
    print("Starting ingestion pipeline...")
    print("=" * 50)

    # Step 1: Fetch articles
    print("\nStep 1: Fetching Wikipedia articles...")
    docs = fetch_wikipedia_articles()

    if not docs:
        print("No documents fetched. Check your internet connection.")
        return

    # Step 2: Chunk documents
    print("\nStep 2: Chunking documents...")
    chunks = chunk_documents(docs)

    # Step 3: Embed and store
    print("\nStep 3: Creating vector store...")
    create_vectorstore(chunks)

    print("\n" + "=" * 50)
    print("Ingestion complete. You can now run the app:")
    print("   streamlit run src/app.py")
    print("=" * 50)


if __name__ == "__main__":
    main()
