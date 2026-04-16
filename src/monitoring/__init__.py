# =========================================
# AI-IPS Monitoring Module
# =========================================

"""
Monitoring package initializer

Provides:
- Security logging
- Event tracking utilities
"""

from .security_logger import SecurityLogger

__all__ = [
    "SecurityLogger"
]