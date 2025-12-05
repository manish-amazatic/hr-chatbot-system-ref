"""
Ingest All Comprehensive HR Policy PDFs into Milvus

Extracts text from all HR policy PDFs, chunks them, generates embeddings,
and stores in Milvus vector database for RAG queries.

Usage:
    python scripts/ingest_all_comprehensive_pdfs.py --drop-existing
"""

import sys
import logging
from pathlib import Path
from pypdf import PdfReader

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from services.milvus_service import MilvusService
from langchain_text_splitters import RecursiveCharacterTextSplitter

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def extract_text_from_pdf(pdf_path: Path) -> str:
    """
    Extract text content from PDF file

    Args:
        pdf_path: Path to PDF file

    Returns:
        Extracted text content
    """
    try:
        reader = PdfReader(str(pdf_path))
        text_content = []

        # Extract text from all pages
        for page_num, page in enumerate(reader.pages, 1):
            page_text = page.extract_text()
            if page_text:
                text_content.append(page_text)

        full_text = "\n\n".join(text_content)
        logger.info("  Extracted %s pages, %s chars", len(reader.pages), len(full_text))

        return full_text

    except Exception as e:
        logger.error("  Error extracting text from PDF: %s", e)
        return ""


def load_policy_pdfs(data_dir: str = "docs/hr_policies_pdf") -> list:
    """
    Load all HR policy PDF documents from directory

    Args:
        data_dir: Directory containing policy PDF files

    Returns:
        List of documents with content and metadata
    """
    data_path = Path(__file__).parent.parent / data_dir

    if not data_path.exists():
        logger.error("Directory not found: %s", data_path.absolute())
        return []

    documents = []

    # Load all .pdf files
    pdf_files = list(data_path.glob("*.pdf"))

    if not pdf_files:
        logger.error("No PDF files found in %s", data_path.absolute())
        return []

    logger.info("Found %s PDF files", len(pdf_files))

    for file_path in sorted(pdf_files):
        try:
            logger.info("Processing: %s", file_path.name)

            # Extract text from PDF
            content = extract_text_from_pdf(file_path)

            if content:
                documents.append({
                    "filename": file_path.name,
                    "content": content,
                    "path": str(file_path)
                })
            else:
                logger.warning("  No content extracted from %s", file_path.name)

        except Exception as e:
            logger.error("Error loading %s: %s", file_path.name, e)

    return documents


def chunk_documents(documents: list, chunk_size: int = 500, chunk_overlap: int = 150) -> list:
    """
    Split documents into smaller chunks for better retrieval

    Args:
        documents: List of documents to chunk
        chunk_size: Maximum chunk size in characters (increased for comprehensive docs)
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
                    "chunk_id": i,
                    "total_chunks": len(chunks),
                    "original_path": doc["path"]
                }
            })

    return chunked_docs


def ingest_to_milvus(chunked_docs: list, drop_existing: bool = False):
    """
    Ingest chunked documents into Milvus

    Args:
        chunked_docs: List of chunked documents
        drop_existing: Whether to drop existing collection
    """
    try:
        milvus_service = MilvusService()

        # Connect to Milvus
        if not milvus_service.connect():
            logger.error("Failed to connect to Milvus")
            logger.error("Make sure Milvus is running: docker ps | grep milvus")
            raise ConnectionError("Milvus connection failed")

        logger.info("✓ Connected to Milvus")

        # Create or recreate collection
        logger.info("\nStep 4: Setting up collection...")
        if not milvus_service.create_collection(drop_existing=drop_existing):
            logger.error("Failed to create collection")
            raise RuntimeError("Collection creation failed")

        logger.info("✓ Collection ready")

        # Ingest in batches
        batch_size = 10
        total_batches = (len(chunked_docs) + batch_size - 1) // batch_size

        logger.info("\nStep 5: Ingesting %s chunks in %s batches...", len(chunked_docs), total_batches)

        for i in range(0, len(chunked_docs), batch_size):
            batch_num = i // batch_size + 1
            batch = chunked_docs[i:i + batch_size]

            try:
                if not milvus_service.insert_documents(batch):
                    logger.error("  Processing batch %s/%s... [FAILED]", batch_num, total_batches)
                    logger.error("  Failed to insert batch")
                else:
                    logger.info("  Processing batch %s/%s... [SUCCESS]", batch_num, total_batches)
            except Exception as e:
                logger.error("  Processing batch %s/%s... [FAILED]", batch_num, total_batches)
                logger.error("  Error: %s", e)

        # Verify ingestion
        total_entities = milvus_service.collection.num_entities
        logger.info("\n✓ Ingestion Complete!")
        logger.info("  Total entities in collection: %s", total_entities)
        return True

    except Exception as e:
        logger.error("Error during Milvus ingestion: %s", e)
        return False


def main(drop_existing: bool = False):
    """
    Main ingestion pipeline

    Args:
        drop_existing: Whether to drop existing collection
    """
    print("==" * 70)
    print("Comprehensive HR Policy PDF Ingestion Pipeline")
    print("=" * 70)

    # Step 1: Load PDF documents
    print("\nStep 1: Loading HR policy PDFs...")
    documents = load_policy_pdfs()

    if not documents:
        logger.error("No documents loaded. Exiting.")
        return

    total_size = sum(len(doc["content"]) for doc in documents)
    logger.info("\n✓ Loaded %s PDF documents", len(documents))
    logger.info("  Total size: %.1f KB", total_size / 1024)

    # Step 2: Chunk documents
    print("\nStep 2: Chunking documents...")
    chunked_docs = chunk_documents(documents, chunk_size=500, chunk_overlap=150)

    avg_chunk_size = sum(len(doc["content"]) for doc in chunked_docs) / len(chunked_docs)
    logger.info("\nCreated %s chunks", len(chunked_docs))
    logger.info("  Avg chunk size: %d chars", int(avg_chunk_size))

    # Step 3: Ingest to Milvus
    print("\nStep 3: Ingesting to Milvus...")
    ingest_to_milvus(chunked_docs, drop_existing=drop_existing)

    print("\n" + "=" * 70)
    print("✓ Comprehensive PDF Ingestion Complete!")
    print("=" * 70)
    print("\nSummary:")
    print("  Documents processed: %s PDFs", len(documents))
    print("  Chunks created: %s", len(chunked_docs))
    print("  Collection: hr_policies")
    print("\nNext steps:")
    print("  1. Test RAG queries: ./test_rag_flow.sh")
    print("  2. The chatbot will now have access to comprehensive HR policies!")
    print()


if __name__ == "__main__":
    # Check for command line arguments
    drop_existing = "--drop-existing" in sys.argv or "-d" in sys.argv

    if drop_existing:
        logger.info("Drop existing collection: YES")
    else:
        logger.info("Drop existing collection: NO (use --drop-existing or -d to drop)")

    main(drop_existing=drop_existing)
