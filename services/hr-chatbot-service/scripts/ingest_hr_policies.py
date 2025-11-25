"""
Script to ingest HR policy documents into Milvus vector database

Usage:
    python scripts/ingest_hr_policies.py [--drop-existing]

Options:
    --drop-existing    Drop existing collection before ingestion
"""

import sys
import json
import logging
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from services.milvus_service import MilvusService
from utils.config import settings

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def load_policy_documents(file_path: str) -> list:
    """
    Load HR policy documents from JSON file

    Args:
        file_path: Path to JSON file containing policy documents

    Returns:
        List of policy documents
    """
    logger.info(f"Loading policy documents from: {file_path}")

    try:
        with open(file_path, 'r') as f:
            documents = json.load(f)

        logger.info(f"Loaded {len(documents)} policy documents")
        return documents

    except FileNotFoundError:
        logger.error(f"File not found: {file_path}")
        return []
    except json.JSONDecodeError as e:
        logger.error(f"Invalid JSON format: {e}")
        return []


def ingest_policies(drop_existing: bool = False):
    """
    Ingest HR policy documents into Milvus

    Args:
        drop_existing: Whether to drop existing collection
    """
    logger.info("=" * 60)
    logger.info("HR Policy Ingestion Script")
    logger.info("=" * 60)

    # Load policy documents
    policy_file = Path(__file__).parent.parent / "data" / "hr_policies" / "sample_policies.json"
    documents = load_policy_documents(str(policy_file))

    if not documents:
        logger.error("No documents to ingest. Exiting.")
        return False

    # Initialize Milvus service
    logger.info("Initializing Milvus service...")
    milvus = MilvusService()

    # Connect to Milvus
    if not milvus.connect():
        logger.error("Failed to connect to Milvus. Please ensure Milvus is running.")
        logger.error(f"Milvus URI: {settings.milvus_uri}")
        logger.error("\nTo start Milvus locally, you can use:")
        logger.error("  docker run -d --name milvus -p 19530:19530 milvusdb/milvus:latest")
        return False

    # Create collection
    logger.info(f"Creating collection: {milvus.collection_name}")
    if not milvus.create_collection(drop_existing=drop_existing):
        logger.error("Failed to create Milvus collection")
        return False

    if drop_existing:
        logger.info("Dropped existing collection")

    # Insert documents
    logger.info(f"Inserting {len(documents)} documents...")
    logger.info("Generating embeddings (this may take a moment)...")

    success = milvus.insert_documents(documents)

    if success:
        logger.info("=" * 60)
        logger.info("✓ Successfully ingested all HR policy documents!")
        logger.info("=" * 60)
        logger.info(f"Collection: {milvus.collection_name}")
        logger.info(f"Documents: {len(documents)}")
        logger.info(f"Embedding Model: {settings.embedding_model}")
        logger.info(f"Dimension: {milvus.dimension}")
        logger.info("=" * 60)

        # Display sample policies
        logger.info("\nSample policies ingested:")
        for i, doc in enumerate(documents[:5], 1):
            title = doc.get('metadata', {}).get('title', 'Untitled')
            category = doc.get('metadata', {}).get('category', 'N/A')
            logger.info(f"  {i}. {title} ({category})")

        if len(documents) > 5:
            logger.info(f"  ... and {len(documents) - 5} more")

        logger.info("\nYou can now query HR policies using the chatbot!")
        return True
    else:
        logger.error("=" * 60)
        logger.error("✗ Failed to ingest HR policy documents")
        logger.error("=" * 60)
        return False


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
