"""
Memory Manager - Utilities for Managing Conversational Memory

This module provides utilities for working with different types of
conversational memory in LangChain applications.

Memory Types Supported:
- ConversationBufferMemory: Stores all messages
- ConversationBufferWindowMemory: Keeps last N messages
- ConversationEntityMemory: Tracks entities
- ConversationSummaryMemory: Summarizes old conversations
"""

from typing import Optional, List, Dict, Any
from enum import Enum
import logging

from langchain_classic.memory import (
    ConversationBufferMemory,
    ConversationBufferWindowMemory,
    ConversationEntityMemory,
    ConversationSummaryMemory
)
from langchain_core.language_models import BaseLanguageModel

logger = logging.getLogger(__name__)


class MemoryType(str, Enum):
    """Enumeration of supported memory types."""
    BUFFER = "buffer"
    WINDOW = "window"
    ENTITY = "entity"
    SUMMARY = "summary"


class MemoryManager:
    """
    Manages different types of conversational memory.
    
    This manager is provider-agnostic and works with any LangChain-compatible LLM.
    
    Usage:
        from core.llm_processor import get_default_llm
        
        manager = MemoryManager()
        memory = manager.create_memory(MemoryType.BUFFER)
        
        # Use with an agent or chain
        llm = get_default_llm()
        memory = manager.create_memory(MemoryType.SUMMARY, llm=llm)
    """
    
    @staticmethod
    def create_memory(
        memory_type: MemoryType = MemoryType.BUFFER,
        llm: Optional[BaseLanguageModel] = None,
        **kwargs
    ):
        """
        Create a memory instance of the specified type.
        
        Args:
            memory_type: Type of memory to create
            llm: LLM instance (required for entity and summary memory)
                 Can be any LangChain-compatible LLM (OpenAI, Anthropic, Google, etc.)
            **kwargs: Additional arguments for memory configuration
                - memory_key: Key for storing memory (default: "chat_history")
                - return_messages: Whether to return message objects (default: True)
                - k: Window size for window memory (default: 5)
                - input_key: Input key for entity memory (default: "input")
            
        Returns:
            Memory instance
            
        Examples:
            from core.llm_processor import LLMProcessor
            
            # Buffer memory (stores all messages)
            memory = MemoryManager.create_memory(MemoryType.BUFFER)
            
            # Window memory (keeps last 5 message pairs)
            memory = MemoryManager.create_memory(MemoryType.WINDOW, k=5)
            
            # Entity memory (requires LLM - tracks entities in conversation)
            processor = LLMProcessor()
            llm = processor.get_llm()
            memory = MemoryManager.create_memory(MemoryType.ENTITY, llm=llm)
            
            # Summary memory (requires LLM - summarizes old conversations)
            memory = MemoryManager.create_memory(MemoryType.SUMMARY, llm=llm)
        """
        memory_key = kwargs.get("memory_key", "chat_history")
        return_messages = kwargs.get("return_messages", True)
        
        logger.debug(
            "Creating memory type: %s (memory_key=%s, return_messages=%s)",
            memory_type.value, memory_key, return_messages
        )
        
        if memory_type == MemoryType.BUFFER:
            return ConversationBufferMemory(
                memory_key=memory_key,
                return_messages=return_messages
            )
        
        elif memory_type == MemoryType.WINDOW:
            k = kwargs.get("k", 5)  # Default window size
            return ConversationBufferWindowMemory(
                k=k,
                memory_key=memory_key,
                return_messages=return_messages
            )
        
        elif memory_type == MemoryType.ENTITY:
            if llm is None:
                raise ValueError(
                    "LLM is required for EntityMemory. "
                    "Use LLMProcessor to get an LLM instance."
                )
            
            input_key = kwargs.get("input_key", "input")
            logger.info("Creating EntityMemory with input_key=%s", input_key)
            return ConversationEntityMemory(
                llm=llm,
                memory_key=memory_key,
                input_key=input_key
            )
        
        elif memory_type == MemoryType.SUMMARY:
            if llm is None:
                raise ValueError(
                    "LLM is required for SummaryMemory. "
                    "Use LLMProcessor to get an LLM instance."
                )
            
            logger.info("Creating SummaryMemory")
            return ConversationSummaryMemory(
                llm=llm,
                memory_key=memory_key,
                return_messages=return_messages
            )
        
        else:
            raise ValueError(f"Unknown memory type: {memory_type}")
    
    @staticmethod
    def get_memory_info(memory) -> Dict[str, Any]:
        """
        Get information about a memory instance.
        
        Args:
            memory: Memory instance
            
        Returns:
            Dictionary with memory info
        """
        info = {
            "type": memory.__class__.__name__,
            "memory_key": getattr(memory, "memory_key", "unknown")
        }
        
        # Add type-specific info
        if isinstance(memory, ConversationBufferWindowMemory):
            info["window_size"] = memory.k
        
        if hasattr(memory, "buffer"):
            info["has_buffer"] = True
            info["buffer_length"] = len(str(memory.buffer))
        
        if hasattr(memory, "chat_memory"):
            info["message_count"] = len(memory.chat_memory.messages)
        
        return info
    
    @staticmethod
    def clear_memory(memory):
        """
        Clear all contents of a memory instance.
        
        Args:
            memory: Memory instance to clear
        """
        logger.debug("Clearing memory: %s", memory.__class__.__name__)
        memory.clear()
    
    @staticmethod
    def export_memory(memory) -> Dict[str, Any]:
        """
        Export memory contents for persistence.
        
        Args:
            memory: Memory instance
            
        Returns:
            Dictionary with memory contents
        """
        export_data = {
            "type": memory.__class__.__name__,
            "memory_key": getattr(memory, "memory_key", "unknown")
        }
        
        if hasattr(memory, "chat_memory"):
            export_data["messages"] = [
                {
                    "type": msg.type,
                    "content": msg.content
                }
                for msg in memory.chat_memory.messages
            ]
        
        if hasattr(memory, "buffer"):
            export_data["buffer"] = str(memory.buffer)
        
        if hasattr(memory, "entity_store"):
            export_data["entities"] = dict(memory.entity_store.store)
        
        return export_data


class ConversationMemoryWrapper:
    """
    High-level wrapper for working with conversational memory.
    
    Provides convenience methods for common memory operations.
    Works with any LangChain-compatible LLM provider.
    
    Usage:
        from core.llm_processor import get_default_llm
        
        # Simple buffer memory
        wrapper = ConversationMemoryWrapper(memory_type=MemoryType.BUFFER)
        wrapper.add_user_message("Hello")
        wrapper.add_ai_message("Hi there!")
        history = wrapper.get_conversation_history()
        
        # Smart memory with LLM
        llm = get_default_llm()
        wrapper = ConversationMemoryWrapper(
            memory_type=MemoryType.SUMMARY,
            llm=llm
        )
    """
    
    def __init__(
        self,
        memory_type: MemoryType = MemoryType.BUFFER,
        llm: Optional[BaseLanguageModel] = None,
        **kwargs
    ):
        """
        Initialize the memory wrapper.
        
        Args:
            memory_type: Type of memory to use
            llm: LLM instance (for entity/summary memory)
                 Can be from any provider (OpenAI, Anthropic, Google, Ollama, Azure)
            **kwargs: Additional memory configuration
        """
        logger.info("Initializing ConversationMemoryWrapper with type: %s", memory_type.value)
        self.memory = MemoryManager.create_memory(
            memory_type=memory_type,
            llm=llm,
            **kwargs
        )
        self.memory_type = memory_type
    
    def add_user_message(self, message: str):
        """Add a user message to memory."""
        if hasattr(self.memory, "chat_memory"):
            self.memory.chat_memory.add_user_message(message)
    
    def add_ai_message(self, message: str):
        """Add an AI message to memory."""
        if hasattr(self.memory, "chat_memory"):
            self.memory.chat_memory.add_ai_message(message)
    
    def get_conversation_history(self) -> List[Dict[str, str]]:
        """
        Get the conversation history.
        
        Returns:
            List of message dictionaries with 'role' and 'content'
        """
        if not hasattr(self.memory, "chat_memory"):
            return []
        
        return [
            {
                "role": msg.type,
                "content": msg.content
            }
            for msg in self.memory.chat_memory.messages
        ]
    
    def get_summary(self) -> str:
        """
        Get a summary of the conversation.
        
        Returns:
            Summary string
        """
        if hasattr(self.memory, "buffer"):
            return str(self.memory.buffer)
        
        # For other memory types, generate a simple summary
        history = self.get_conversation_history()
        if not history:
            return "No conversation yet"
        
        return f"Conversation with {len(history)} messages"
    
    def get_entities(self) -> Dict[str, str]:
        """
        Get extracted entities (only for EntityMemory).
        
        Returns:
            Dictionary of entities
        """
        if hasattr(self.memory, "entity_store"):
            return dict(self.memory.entity_store.store)
        return {}
    
    def clear(self):
        """Clear the memory."""
        self.memory.clear()
    
    def get_info(self) -> Dict[str, Any]:
        """Get information about the memory."""
        return MemoryManager.get_memory_info(self.memory)
    
    def export(self) -> Dict[str, Any]:
        """Export memory contents."""
        return MemoryManager.export_memory(self.memory)


# Convenience functions

def create_simple_memory(window_size: Optional[int] = None):
    """
    Create a simple memory instance.
    
    Args:
        window_size: If provided, creates window memory; otherwise buffer memory
        
    Returns:
        Memory instance
        
    Example:
        # Buffer memory (unlimited)
        memory = create_simple_memory()
        
        # Window memory (last 5 messages)
        memory = create_simple_memory(window_size=5)
    """
    if window_size:
        return MemoryManager.create_memory(MemoryType.WINDOW, k=window_size)
    else:
        return MemoryManager.create_memory(MemoryType.BUFFER)


def create_smart_memory(llm: BaseLanguageModel, use_entities: bool = False):
    """
    Create an intelligent memory instance.
    
    Works with any LangChain-compatible LLM (OpenAI, Anthropic, Google, Ollama, Azure).
    
    Args:
        llm: LLM instance from any provider
        use_entities: If True, creates entity memory; otherwise summary memory
        
    Returns:
        Memory instance
        
    Example:
        from core.llm_processor import LLMProcessor
        
        processor = LLMProcessor()
        llm = processor.get_llm()  # Uses configured provider
        
        # Entity memory (tracks people, places, organizations, etc.)
        memory = create_smart_memory(llm, use_entities=True)
        
        # Summary memory (compacts old messages to save tokens)
        memory = create_smart_memory(llm, use_entities=False)
    """
    memory_type = MemoryType.ENTITY if use_entities else MemoryType.SUMMARY
    logger.info("Creating smart memory: %s", memory_type.value)
    return MemoryManager.create_memory(memory_type, llm=llm)

