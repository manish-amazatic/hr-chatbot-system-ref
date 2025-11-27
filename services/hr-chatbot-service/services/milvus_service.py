"""
Milvus Service - Multi-Provider Embeddings
Handles vector database operations for RAG with support for multiple embedding providers
"""
import logging
from typing import List, Dict, Any, Optional
from pymilvus import connections, Collection, FieldSchema, CollectionSchema, DataType, utility

from langchain_openai import OpenAIEmbeddings, AzureOpenAIEmbeddings
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_ollama import OllamaEmbeddings

from core.config import settings

logger = logging.getLogger(__name__)


class MilvusService:
    """
    Service for Milvus vector database operations with multi-provider embeddings

    Supports:
    - OpenAI embeddings (text-embedding-3-small/large, ada-002)
    - Azure OpenAI embeddings
    - Anthropic embeddings (Voyage AI)
    - Google embeddings (text-embedding-004)
    - Ollama embeddings (nomic-embed-text, mxbai-embed-large)

    Provides functionality for:
    - Connecting to Milvus
    - Creating collections
    - Storing document embeddings
    - Similarity search for RAG
    """

    def __init__(self):
        """Initialize Milvus service with configured embedding provider"""
        self.collection_name = settings.milvus_collection_name
        self.embedding_model = self._create_embedding_model()
        self.dimension = settings.embedding_dimensions or 1536
        self.collection = None
        self._connected = False

        logger.info(
            f"MilvusService initialized with {settings.embedding_provider} "
            f"embeddings (model: {settings.embedding_model}, dim: {self.dimension})"
        )

    def _create_embedding_model(self):
        """
        Create embedding model based on configured provider

        Returns:
            Embedding model instance
        """
        provider = settings.embedding_provider
        model = settings.embedding_model

        logger.info(f"Creating embedding model: {provider} - {model}")

        if provider == "openai":
            return self._create_openai_embeddings(model)
        elif provider == "azure":
            return self._create_azure_embeddings(model)
        elif provider == "anthropic":
            return self._create_anthropic_embeddings(model)
        elif provider == "google":
            return self._create_google_embeddings(model)
        elif provider == "ollama":
            return self._create_ollama_embeddings(model)
        else:
            raise ValueError(f"Unsupported embedding provider: {provider}")

    def _create_openai_embeddings(self, model: str) -> OpenAIEmbeddings:
        """Create OpenAI embeddings instance"""
        params = {
            "model": model,
            "openai_api_key": settings.openai_api_key,
        }

        if settings.openai_base_url:
            params["openai_api_base"] = settings.openai_base_url
        if settings.openai_organization:
            params["openai_organization"] = settings.openai_organization

        return OpenAIEmbeddings(**params)

    def _create_azure_embeddings(self, model: str) -> AzureOpenAIEmbeddings:
        """Create Azure OpenAI embeddings instance"""
        return AzureOpenAIEmbeddings(
            azure_deployment=settings.azure_openai_embedding_deployment_name or model,
            azure_endpoint=settings.azure_openai_endpoint,
            api_key=settings.azure_openai_api_key,
            api_version=settings.azure_openai_api_version,
        )

    def _create_anthropic_embeddings(self, model: str):
        """
        Anthropic embeddings not directly supported

        Note: Anthropic partners with Voyage AI for embeddings.
        Use OpenAI embeddings with Anthropic LLM for best compatibility.
        """
        raise NotImplementedError(
            "Anthropic doesn't provide embeddings directly. "
            "They partner with Voyage AI for embeddings. "
            "Please use 'openai' as embedding_provider with Anthropic LLM, "
            "or install and configure Voyage AI embeddings separately."
        )

    def _create_google_embeddings(self, model: str) -> GoogleGenerativeAIEmbeddings:
        """Create Google embeddings instance"""
        params = {
            "model": model,
            "google_api_key": settings.google_api_key,
        }

        if settings.google_project_id:
            params["project"] = settings.google_project_id

        return GoogleGenerativeAIEmbeddings(**params)

    def _create_ollama_embeddings(self, model: str) -> OllamaEmbeddings:
        """Create Ollama (local) embeddings instance"""
        return OllamaEmbeddings(
            model=model,
            base_url=settings.ollama_base_url,
        )

    def connect(self) -> bool:
        """
        Connect to Milvus server

        Returns:
            bool: True if connected successfully, False otherwise
        """
        try:
            # Parse Milvus URI
            uri = settings.milvus_uri
            if uri.startswith("http://"):
                uri = uri.replace("http://", "")
            elif uri.startswith("https://"):
                uri = uri.replace("https://", "")

            # Split host and port
            if ":" in uri:
                host, port = uri.split(":")
                port = int(port)
            else:
                host = uri
                port = 19530

            # Connect to Milvus
            connections.connect(
                alias="default",
                host=host,
                port=port,
                token=settings.milvus_token if settings.milvus_token else None
            )

            self._connected = True
            logger.info(f"Connected to Milvus at {host}:{port}")
            return True

        except Exception as e:
            logger.warning(f"Failed to connect to Milvus: {e}")
            self._connected = False
            return False

    def create_collection(self, drop_existing: bool = False) -> bool:
        """
        Create Milvus collection for HR policies

        Args:
            drop_existing: Whether to drop existing collection

        Returns:
            bool: True if created successfully
        """
        try:
            if not self._connected:
                if not self.connect():
                    return False

            # Drop existing collection if requested
            if drop_existing and utility.has_collection(self.collection_name):
                utility.drop_collection(self.collection_name)
                logger.info(f"Dropped existing collection: {self.collection_name}")

            # Check if collection already exists
            if utility.has_collection(self.collection_name):
                self.collection = Collection(self.collection_name)
                logger.info(f"Using existing collection: {self.collection_name}")
                return True

            # Define schema
            fields = [
                FieldSchema(name="id", dtype=DataType.INT64, is_primary=True, auto_id=True),
                FieldSchema(name="document_id", dtype=DataType.VARCHAR, max_length=100),
                FieldSchema(name="content", dtype=DataType.VARCHAR, max_length=5000),
                FieldSchema(name="metadata", dtype=DataType.JSON),
                FieldSchema(name="embedding", dtype=DataType.FLOAT_VECTOR, dim=self.dimension)
            ]

            schema = CollectionSchema(
                fields=fields,
                description="HR policy documents with embeddings"
            )

            # Create collection
            self.collection = Collection(
                name=self.collection_name,
                schema=schema
            )

            # Create index on vector field
            index_params = {
                "metric_type": "L2",
                "index_type": "IVF_FLAT",
                "params": {"nlist": 128}
            }

            self.collection.create_index(
                field_name="embedding",
                index_params=index_params
            )

            logger.info(f"Created collection: {self.collection_name}")
            return True

        except Exception as e:
            logger.error(f"Error creating collection: {e}")
            return False

    def insert_documents(
        self,
        documents: List[Dict[str, Any]]
    ) -> bool:
        """
        Insert documents into Milvus

        Args:
            documents: List of documents with 'content' and 'metadata'

        Returns:
            bool: True if inserted successfully
        """
        try:
            if not self.collection:
                if not self.create_collection():
                    return False

            # Generate embeddings
            texts = [doc["content"] for doc in documents]
            embeddings = self.embedding_model.embed_documents(texts)

            # Prepare data
            data = []
            for i, doc in enumerate(documents):
                data.append({
                    "document_id": doc.get("id", f"doc_{i}"),
                    "content": doc["content"],
                    "metadata": doc.get("metadata", {}),
                    "embedding": embeddings[i]
                })

            # Insert into collection
            self.collection.insert(data)
            self.collection.flush()

            logger.info(f"Inserted {len(documents)} documents into Milvus")
            return True

        except Exception as e:
            logger.error(f"Error inserting documents: {e}")
            return False

    def search(
        self,
        query: str,
        k: int = 3,
        similarity_threshold: float = 0.7
    ) -> List[Dict[str, Any]]:
        """
        Search for similar documents using vector similarity

        Args:
            query: Search query text
            k: Number of results to return
            similarity_threshold: Minimum similarity score

        Returns:
            List of matching documents with scores
        """
        try:
            if not self.collection:
                if not self.create_collection():
                    return []

            # Load collection into memory
            self.collection.load()

            # Generate query embedding
            query_embedding = self.embedding_model.embed_query(query)

            # Search parameters
            search_params = {
                "metric_type": "L2",
                "params": {"nprobe": 10}
            }

            # Perform search
            results = self.collection.search(
                data=[query_embedding],
                anns_field="embedding",
                param=search_params,
                limit=k,
                output_fields=["document_id", "content", "metadata"]
            )

            # Format results
            formatted_results = []
            for hits in results:
                for hit in hits:
                    # Convert L2 distance to similarity score (0-1)
                    # Lower L2 distance = higher similarity
                    similarity = 1 / (1 + hit.distance)

                    if similarity >= similarity_threshold:
                        formatted_results.append({
                            "document_id": hit.entity.document_id,
                            "content": hit.entity.content,
                            "metadata": hit.entity.metadata,
                            "score": similarity,
                            "distance": hit.distance
                        })

            logger.info(f"Found {len(formatted_results)} results for query: {query[:50]}...")
            return formatted_results

        except Exception as e:
            logger.error(f"Error searching: {e}")
            return []

    def close(self):
        """Close Milvus connection"""
        try:
            if self._connected:
                connections.disconnect("default")
                self._connected = False
                logger.info("Disconnected from Milvus")
        except Exception as e:
            logger.error(f"Error closing Milvus connection: {e}")

    def is_available(self) -> bool:
        """Check if Milvus is available"""
        if not self._connected:
            return self.connect()
        return self._connected

    def get_embedding_provider(self) -> str:
        """Get the current embedding provider"""
        return settings.embedding_provider

    def get_embedding_model(self) -> str:
        """Get the current embedding model"""
        return settings.embedding_model

    def get_embedding_dimensions(self) -> int:
        """Get the embedding dimensions"""
        return self.dimension
