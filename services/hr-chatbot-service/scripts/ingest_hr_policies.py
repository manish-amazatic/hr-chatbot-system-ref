"""
Script to ingest HR policy documents into Milvus vector database

Reads HR policy text files, chunks them, and stores embeddings in Milvus for RAG.

Usage:
    python scripts/ingest_hr_policies.py [--drop-existing]

Options:
    --drop-existing    Drop existing collection before ingestion
"""

import sys
import logging
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from services.milvus_service import MilvusService
from langchain.text_splitter import RecursiveCharacterTextSplitter

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def load_policy_documents(data_dir: str = "data/hr_policies") -> list:
    """
    Load all HR policy documents from directory

    Args:
        data_dir: Directory containing policy text files

    Returns:
        List of documents with content and metadata
    """
    data_path = Path(__file__).parent.parent / data_dir

    if not data_path.exists():
        logger.error(f"Directory not found: {data_path.absolute()}")
        return []

    documents = []

    # Load all .txt files
    for file_path in data_path.glob("*.txt"):
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            documents.append({
                "filename": file_path.name,
                "content": content,
                "path": str(file_path)
            })

            logger.info(f"Loaded: {file_path.name} ({len(content)} chars)")

        except Exception as e:
            logger.error(f"Error loading {file_path.name}: {e}")

    return documents


def chunk_documents(documents: list, chunk_size: int = 1000, chunk_overlap: int = 200) -> list:
    """
    Split documents into smaller chunks for better retrieval

    Args:
        documents: List of documents to chunk
        chunk_size: Maximum chunk size in characters
        chunk_overlap: Overlap between chunks

    Returns:
        List of chunked documents with metadata
    """
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        separators=["\n\n", "\n", ".", "!", "?", " ", ""],
        length_function=len
    )

    chunked_docs = []

    for doc in documents:
        # Split document into chunks
        chunks = text_splitter.split_text(doc["content"])

        # Create chunk documents with metadata
        for i, chunk in enumerate(chunks):
            chunked_docs.append({
                "id": f"{doc['filename']}_chunk_{i}",
                "content": chunk,
                "metadata": {
                    "source": doc["filename"],
                    "chunk_index": i,
                    "total_chunks": len(chunks),
                    "path": doc["path"]
                }
            })

        logger.info(f"Chunked: {doc['filename']} into {len(chunks)} parts")

    return chunked_docs


def ingest_policies(drop_existing: bool = False):
    """
    Ingest HR policy documents into Milvus

    Args:
        drop_existing: Whether to drop existing collection
    """
    logger.info("=" * 70)
    logger.info("HR Policy Ingestion Script")
    logger.info("=" * 70)

    # Step 1: Load documents
    logger.info("\nStep 1: Loading HR policy documents...")
    documents = load_policy_documents()

    if not documents:
        logger.error("No documents found. Please run generate_hr_policies.py first.")
        return False

    logger.info(f"✓ Loaded {len(documents)} policy documents")
    logger.info(f"  Total size: {sum(len(d['content']) for d in documents) / 1024:.1f} KB")

    # Step 2: Chunk documents
    logger.info("\nStep 2: Chunking documents...")
    chunked_docs = chunk_documents(documents, chunk_size=1000, chunk_overlap=200)
    logger.info(f"✓ Created {len(chunked_docs)} chunks")
    avg_chunk_size = sum(len(d['content']) for d in chunked_docs) / len(chunked_docs)
    logger.info(f"  Avg chunk size: {avg_chunk_size:.0f} chars")

    # Step 3: Initialize Milvus
    logger.info("\nStep 3: Connecting to Milvus...")
    milvus = MilvusService()

    if not milvus.connect():
        logger.error("Failed to connect to Milvus")
        logger.error("Make sure Milvus is running: docker-compose up -d milvus-standalone")
        return False

    # Create collection
    logger.info("Creating collection...")
    if not milvus.create_collection(drop_existing=drop_existing):
        logger.error("Failed to create collection")
        return False

    if drop_existing:
        logger.info("Dropped existing collection")

    # Step 4: Insert documents
    logger.info("\nStep 4: Ingesting to Milvus...")
    logger.info("(Generating embeddings - this may take a few minutes...)")

    # Insert in batches
    batch_size = 10
    total_batches = (len(chunked_docs) + batch_size - 1) // batch_size

    for i in range(0, len(chunked_docs), batch_size):
        batch = chunked_docs[i:i + batch_size]
        batch_num = i // batch_size + 1

        logger.info(f"Processing batch {batch_num}/{total_batches}...")

        if not milvus.insert_documents(batch):
            logger.error(f"Failed to insert batch {batch_num}")
            return False

    # Step 5: Test search
    logger.info("\nStep 5: Testing search functionality...")
    test_queries = [
        "How many days of annual leave do I get?",
        "What is the work from home policy?",
        "How is performance evaluated?"
    ]

    for query in test_queries:
        results = milvus.search(query, k=2)
        logger.info(f"\nQuery: {query}")
        logger.info(f"Found {len(results)} results")
        if results:
            logger.info(f"Top result: {results[0]['document_id']} (score: {results[0]['score']:.3f})")

    # Success summary
    logger.info("\n" + "=" * 70)
    logger.info("✓ Ingestion Complete!")
    logger.info("=" * 70)
    logger.info(f"Documents: {len(documents)} files → {len(chunked_docs)} chunks")
    logger.info(f"Collection: {milvus.collection_name}")
    logger.info("\nYou can now query HR policies using the chatbot!")
    logger.info("=" * 70)

    return True


def main():
    """Main entry point"""
    import argparse

    parser = argparse.ArgumentParser(
        description="Ingest HR policy documents into Milvus vector database"
    )
    parser.add_argument(
        "--drop-existing",
        action="store_true",
        help="Drop existing collection before ingestion"
    )

    args = parser.parse_args()

    # Run ingestion
    success = ingest_policies(drop_existing=args.drop_existing)

    # Exit with appropriate code
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
