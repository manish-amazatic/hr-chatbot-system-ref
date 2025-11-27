"""
Configuration compatibility module

This module re-exports configuration from core.config for backward compatibility.
All configuration is now centralized in core.config.
"""
from core.config import Settings, settings, get_settings

__all__ = ["Settings", "settings", "get_settings"]
