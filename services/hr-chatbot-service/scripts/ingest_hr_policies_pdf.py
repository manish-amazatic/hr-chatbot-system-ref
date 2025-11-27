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
        logger.info(f"  Extracted {len(reader.pages)} pages, {len(full_text)} chars")

        return full_text

    except Exception as e:
        logger.error(f"  Error extracting text from PDF: {e}")
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
        logger.error(f"Directory not found: {data_path.absolute()}")
        return []

    documents = []

    # Load all .pdf files
    pdf_files = list(data_path.glob("*.pdf"))

    if not pdf_files:
        logger.error(f"No PDF files found in {data_path.absolute()}")
        return []

    logger.info(f"Found {len(pdf_files)} PDF files")

    for file_path in sorted(pdf_files):
        try:
            logger.info(f"Processing: {file_path.name}")

            # Extract text from PDF
            content = extract_text_from_pdf(file_path)

            if content:
                documents.append({
                    "filename": file_path.name,
                    "content": content,
                    "path": str(file_path)
                })
            else:
                logger.warning(f"  No content extracted from {file_path.name}")

        except Exception as e:
            logger.error(f"Error loading {file_path.name}: {e}")

    return documents


def chunk_documents(documents: list, chunk_size: int = 1500, chunk_overlap: int = 300) -> list:
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

        logger.info(f"\nStep 5: Ingesting {len(chunked_docs)} chunks in {total_batches} batches...")

        for i in range(0, len(chunked_docs), batch_size):
            batch_num = i // batch_size + 1
            batch = chunked_docs[i:i + batch_size]

            try:
                if not milvus_service.insert_documents(batch):
                    logger.error(f"  Processing batch {batch_num}/{total_batches}... [FAILED]")
                    logger.error(f"  Failed to insert batch")
                else:
                    logger.info(f"  Processing batch {batch_num}/{total_batches}... [SUCCESS]")
            except Exception as e:
                logger.error(f"  Processing batch {batch_num}/{total_batches}... [FAILED]")
                logger.error(f"  Error: {e}")

        # Verify ingestion
        total_entities = milvus_service.collection.num_entities
        logger.info(f"\n✓ Ingestion Complete!")
        logger.info(f"  Total entities in collection: {total_entities}")

        return True

    except Exception as e:
        logger.error(f"Error during Milvus ingestion: {e}")
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
    logger.info(f"\n✓ Loaded {len(documents)} PDF documents")
    logger.info(f"  Total size: {total_size / 1024:.1f} KB")

    # Step 2: Chunk documents
    print("\nStep 2: Chunking documents...")
    chunked_docs = chunk_documents(documents, chunk_size=1500, chunk_overlap=300)

    avg_chunk_size = sum(len(doc["content"]) for doc in chunked_docs) / len(chunked_docs)
    logger.info(f"\n✓ Created {len(chunked_docs)} chunks")
    logger.info(f"  Avg chunk size: {int(avg_chunk_size)} chars")

    # Step 3: Ingest to Milvus
    print("\nStep 3: Ingesting to Milvus...")
    ingest_to_milvus(chunked_docs, drop_existing=drop_existing)

    print("\n" + "=" * 70)
    print("✓ Comprehensive PDF Ingestion Complete!")
    print("=" * 70)
    print(f"\nSummary:")
    print(f"  Documents processed: {len(documents)} PDFs")
    print(f"  Chunks created: {len(chunked_docs)}")
    print(f"  Collection: hr_policies")
    print(f"\nNext steps:")
    print("  1. Test RAG queries: ./test_rag_flow.sh")
    print("  2. The chatbot will now have access to comprehensive HR policies!")
    print()


if __name__ == "__main__":
    # Check for command line arguments
    drop_existing = "--drop-existing" in sys.argv

    if drop_existing:
        logger.info("Drop existing collection: YES")
    else:
        logger.info("Drop existing collection: NO (use --drop-existing to drop)")

    main(drop_existing=drop_existing)
