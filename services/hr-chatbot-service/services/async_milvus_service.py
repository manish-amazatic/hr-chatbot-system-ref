"""
Async Milvus Service - Multi-Provider Embeddings
Handles async vector database operations for RAG with support for multiple embedding providers
"""
import logging
from typing import List, Dict, Any, Optional

from pymilvus import DataType
from pymilvus.milvus_client.async_milvus_client import AsyncMilvusClient
from pymilvus.milvus_client.index import IndexParams

from langchain_openai import OpenAIEmbeddings, AzureOpenAIEmbeddings
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_ollama import OllamaEmbeddings

from core.config import settings

logger = logging.getLogger(__name__)


class AsyncMilvusService:
    """
    Async service for Milvus vector database operations with multi-provider embeddings

    Supports:
    - OpenAI embeddings (text-embedding-3-small/large, ada-002)
    - Azure OpenAI embeddings
    - Anthropic embeddings (Voyage AI)
    - Google embeddings (text-embedding-004)
    - Ollama embeddings (nomic-embed-text, mxbai-embed-large)

    Provides async functionality for:
    - Connecting to Milvus
    - Creating collections
    - Storing document embeddings
    - Similarity search for RAG
    """

    def __init__(self):
        """Initialize async Milvus service with configured embedding provider"""
        self.collection_name = settings.milvus_collection_name
        self.embedding_model = self._create_embedding_model()
        self.dimension = settings.embedding_dimensions or 1536
        self.client: Optional[AsyncMilvusClient] = None
        self._connected = False

        logger.info(
            f"AsyncMilvusService initialized with {settings.embedding_provider} "
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

    async def connect(self) -> bool:
        """
        Connect to Milvus server asynchronously

        Returns:
            bool: True if connected successfully, False otherwise
        """
        try:
            # Parse Milvus URI
            uri = settings.milvus_uri

            # Prepare connection parameters
            connection_params = {
                "uri": uri,
            }

            if settings.milvus_token:
                connection_params["token"] = settings.milvus_token

            # Create async client
            self.client = AsyncMilvusClient(**connection_params)
            self._connected = True

            logger.info(f"Connected to Milvus at {uri}")
            return True

        except Exception as e:
            logger.warning(f"Failed to connect to Milvus: {e}")
            self._connected = False
            return False

    async def create_collection(self, drop_existing: bool = False) -> bool:
        """
        Create Milvus collection for HR policies asynchronously

        Args:
            drop_existing: Whether to drop existing collection

        Returns:
            bool: True if created successfully
        """
        try:
            if not self._connected:
                if not await self.connect():
                    return False

            # Drop existing collection if requested
            if drop_existing:
                has_collection = await self.client.has_collection(self.collection_name)
                if has_collection:
                    await self.client.drop_collection(self.collection_name)
                    logger.info(f"Dropped existing collection: {self.collection_name}")

            # Check if collection already exists
            has_collection = await self.client.has_collection(self.collection_name)
            if has_collection:
                logger.info(f"Using existing collection: {self.collection_name}")
                return True

            # Create schema with custom fields
            schema = AsyncMilvusClient.create_schema(
                auto_id=True,
                enable_dynamic_field=True,
            )

            # Add fields
            schema.add_field(
                field_name="id",
                datatype=DataType.INT64,
                is_primary=True,
                auto_id=True,
            )
            schema.add_field(
                field_name="document_id",
                datatype=DataType.VARCHAR,
                max_length=100,
            )
            schema.add_field(
                field_name="content",
                datatype=DataType.VARCHAR,
                max_length=5000,
            )
            schema.add_field(
                field_name="metadata",
                datatype=DataType.JSON,
            )
            schema.add_field(
                field_name="embedding",
                datatype=DataType.FLOAT_VECTOR,
                dim=self.dimension,
            )

            # Create index parameters
            index_params = IndexParams()
            index_params.add_index(
                field_name="embedding",
                index_type="IVF_FLAT",
                metric_type="L2",
                params={"nlist": 128}
            )

            # Create collection with schema and index
            await self.client.create_collection(
                collection_name=self.collection_name,
                schema=schema,
                index_params=index_params,
            )

            logger.info(f"Created collection: {self.collection_name}")
            return True

        except Exception as e:
            logger.error(f"Error creating collection: {e}")
            return False

    async def insert_documents(
        self,
        documents: List[Dict[str, Any]]
    ) -> bool:
        """
        Insert documents into Milvus asynchronously

        Args:
            documents: List of documents with 'content' and 'metadata'

        Returns:
            bool: True if inserted successfully
        """
        try:
            if not self.client:
                if not await self.create_collection():
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
            result = await self.client.insert(
                collection_name=self.collection_name,
                data=data
            )

            # Flush to ensure data is persisted
            await self.client.flush(self.collection_name)

            logger.info(f"Inserted {len(documents)} documents into Milvus")
            return True

        except Exception as e:
            logger.error(f"Error inserting documents: {e}")
            return False

    async def search(
        self,
        query: str,
        k: int = 3,
        similarity_threshold: float = 0.7
    ) -> List[Dict[str, Any]]:
        """
        Search for similar documents using vector similarity asynchronously

        Args:
            query: Search query text
            k: Number of results to return
            similarity_threshold: Minimum similarity score

        Returns:
            List of matching documents with scores
        """
        try:
            if not self.client:
                if not await self.create_collection():
                    return []

            # Load collection into memory
            await self.client.load_collection(self.collection_name)

            # Generate query embedding
            query_embedding = self.embedding_model.embed_query(query)

            # Search parameters
            search_params = {
                "metric_type": "L2",
                "params": {"nprobe": 10}
            }

            # Perform search
            results = await self.client.search(
                collection_name=self.collection_name,
                data=[query_embedding],
                anns_field="embedding",
                search_params=search_params,
                limit=k,
                output_fields=["document_id", "content", "metadata"]
            )

            # Format results
            formatted_results = []
            for hits in results:
                for hit in hits:
                    # Convert L2 distance to similarity score (0-1)
                    # Lower L2 distance = higher similarity
                    distance = hit.get("distance", 0)
                    similarity = 1 / (1 + distance)

                    if similarity >= similarity_threshold:
                        formatted_results.append({
                            "document_id": hit.get("document_id"),
                            "content": hit.get("content"),
                            "metadata": hit.get("metadata", {}),
                            "score": similarity,
                            "distance": distance
                        })

            logger.info(f"Found {len(formatted_results)} results for query: {query[:50]}...")
            return formatted_results

        except Exception as e:
            logger.error(f"Error searching: {e}")
            return []

    async def close(self):
        """Close Milvus connection asynchronously"""
        try:
            if self._connected and self.client:
                await self.client.close()
                self._connected = False
                logger.info("Disconnected from Milvus")
        except Exception as e:
            logger.error(f"Error closing Milvus connection: {e}")

    async def is_available(self) -> bool:
        """Check if Milvus is available asynchronously"""
        if not self._connected:
            return await self.connect()
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

    async def delete_documents(
        self,
        document_ids: Optional[List[str]] = None,
        filter_expr: Optional[str] = None
    ) -> bool:
        """
        Delete documents from the collection asynchronously

        Args:
            document_ids: List of document IDs to delete
            filter_expr: Filter expression for deletion

        Returns:
            bool: True if deleted successfully
        """
        try:
            if not self.client:
                logger.warning("Client not connected")
                return False

            if document_ids:
                # Create filter expression for document IDs
                ids_str = "', '".join(document_ids)
                filter_expr = f"document_id in ['{ids_str}']"

            if not filter_expr:
                logger.warning("No document IDs or filter provided for deletion")
                return False

            result = await self.client.delete(
                collection_name=self.collection_name,
                filter=filter_expr
            )

            deleted_count = result.get("delete_count", 0)
            logger.info(f"Deleted {deleted_count} documents from Milvus")
            return True

        except Exception as e:
            logger.error(f"Error deleting documents: {e}")
            return False

    async def get_collection_stats(self) -> Dict[str, Any]:
        """
        Get collection statistics asynchronously

        Returns:
            Dict with collection statistics
        """
        try:
            if not self.client:
                if not await self.connect():
                    return {}

            stats = await self.client.get_collection_stats(self.collection_name)
            return stats

        except Exception as e:
            logger.error(f"Error getting collection stats: {e}")
            return {}

    async def query_documents(
        self,
        filter_expr: str,
        output_fields: Optional[List[str]] = None,
        limit: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """
        Query documents by filter expression asynchronously

        Args:
            filter_expr: Filter expression
            output_fields: Fields to return
            limit: Maximum number of results

        Returns:
            List of matching documents
        """
        try:
            if not self.client:
                if not await self.connect():
                    return []

            query_params = {
                "collection_name": self.collection_name,
                "filter": filter_expr,
            }

            if output_fields:
                query_params["output_fields"] = output_fields

            results = await self.client.query(**query_params)

            if limit:
                results = results[:limit]

            return results

        except Exception as e:
            logger.error(f"Error querying documents: {e}")
            return []

    async def __aenter__(self):
        """Async context manager entry"""
        await self.connect()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        await self.close()
