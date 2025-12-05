"""
HR Chatbot Service - Main FastAPI Application
Entry point for the agentic chatbot service
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import logging

from core.config import settings
from api.routes import chat


# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.log_level.upper()),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan events for startup and shutdown"""
    # Startup
    logger.info("Starting %s %s v%s", settings.app_name, settings.app_name, settings.app_version)
    logger.info("LLM Provider: %s", settings.llm_provider)
    logger.info("LLM Model: %s", settings.llm_model)
    logger.info("Milvus URI: %s", settings.milvus_uri)
    logger.info("Embedding Provider: %s", settings.embedding_provider)
    logger.info("Embedding Model: %s", settings.embedding_model)

    # TODO: Connect to Milvus
    # TODO: Load agents

    yield

    # Shutdown
    logger.info("Shutting down HR Chatbot Service")


# Create FastAPI application
app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="Agentic HR Chatbot with RAG capabilities",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(chat.router, prefix="/api/v1/chat", tags=["Chat"])


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "service": settings.app_name,
        "version": settings.app_version,
        "status": "running",
        "docs": "/docs"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "api.main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.reload
    )
