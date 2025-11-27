"""
Utility modules

Compatibility layer: Re-exports settings from core.config for backward compatibility.
Old imports like `from utils.config import settings` will still work.
"""
from core.config import settings, get_settings

__all__ = ["settings", "get_settings"]
