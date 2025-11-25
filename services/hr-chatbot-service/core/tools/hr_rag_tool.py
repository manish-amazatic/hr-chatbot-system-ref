"""
HR RAG Tool
LangChain tool for searching HR policies using RAG
"""
import logging
from typing import Optional
from langchain.tools import tool

from services.milvus_service import MilvusService
from core.processors.llm_processor import LLMProcessor, LLMProvider

logger = logging.getLogger(__name__)

# Global Milvus service instance (singleton pattern)
_milvus_service: Optional[MilvusService] = None


def get_milvus_service() -> MilvusService:
    """Get or create Milvus service instance"""
    global _milvus_service
    if _milvus_service is None:
        _milvus_service = MilvusService()
    return _milvus_service


@tool
def search_hr_policies(query: str) -> str:
    """
    Search HR policies and company guidelines using RAG.

    Use this tool when the user asks about:
    - Company policies
    - HR rules and regulations
    - Employee guidelines
    - Procedures and processes
    - FAQ about company policies

    Args:
        query: The question about HR policies

    Returns:
        Answer based on company HR policies and guidelines
    """
    try:
        logger.info(f"Searching HR policies for: {query[:100]}...")

        # Get Milvus service
        milvus = get_milvus_service()

        # Check if Milvus is available
        if not milvus.is_available():
            return (
                "I apologize, but the HR policy search system is currently unavailable. "
                "Please contact HR directly for policy-related questions, or try again later."
            )

        # Search for relevant documents
        results = milvus.search(query, k=3, similarity_threshold=0.5)

        if not results:
            return (
                "I couldn't find specific information about that in our HR policies. "
                "This might be a new topic or phrased differently than our documentation. "
                "Please contact HR directly at hr@company.com for clarification."
            )

        # Format context from search results
        context = format_search_results(results)

        # Generate answer using LLM with context
        llm = LLMProcessor().get_llm(LLMProvider.OPENAI)

        prompt = f"""You are a helpful HR assistant. Based on the following company policy documents, answer the user's question.

Company Policy Context:
{context}

User Question: {query}

Instructions:
- Provide a clear, concise answer based on the policy documents above
- If the policy documents don't fully answer the question, acknowledge this
- Be professional and helpful
- If specific details are missing, suggest contacting HR

Answer:"""

        response = llm.invoke(prompt)

        # Extract content from response
        answer = response.content if hasattr(response, 'content') else str(response)

        # Add source attribution
        answer += "\n\n---\nBased on company HR policies and guidelines."

        logger.info(f"Generated HR policy answer ({len(results)} sources)")
        return answer

    except Exception as e:
        logger.error(f"Error in search_hr_policies: {str(e)}", exc_info=True)
        return (
            f"I encountered an error while searching HR policies: {str(e)}. "
            "Please try rephrasing your question or contact HR directly."
        )


def format_search_results(results: list) -> str:
    """
    Format Milvus search results into context string

    Args:
        results: List of search results from Milvus

    Returns:
        Formatted context string
    """
    context = ""
    for i, result in enumerate(results, 1):
        content = result.get("content", "")
        score = result.get("score", 0)
        metadata = result.get("metadata", {})

        # Add document info
        context += f"\n\n[Document {i}] (Relevance: {score:.2f})\n"

        # Add metadata if available
        if metadata:
            if "title" in metadata:
                context += f"Title: {metadata['title']}\n"
            if "category" in metadata:
                context += f"Category: {metadata['category']}\n"

        # Add content
        context += f"Content: {content}\n"

    return context


def ingest_hr_policies(policy_documents: list) -> bool:
    """
    Ingest HR policy documents into Milvus

    Args:
        policy_documents: List of policy documents to ingest
            Each document should have: {id, content, metadata}

    Returns:
        bool: True if ingestion successful
    """
    try:
        milvus = get_milvus_service()

        if not milvus.is_available():
            logger.error("Milvus not available for ingestion")
            return False

        # Create collection if needed
        if not milvus.create_collection():
            logger.error("Failed to create Milvus collection")
            return False

        # Insert documents
        success = milvus.insert_documents(policy_documents)

        if success:
            logger.info(f"Successfully ingested {len(policy_documents)} HR policy documents")
        else:
            logger.error("Failed to ingest HR policy documents")

        return success

    except Exception as e:
        logger.error(f"Error ingesting HR policies: {e}", exc_info=True)
        return False
