"""
Claim Pilot Core

Shared configuration, database utilities, exceptions, and core components.
Logging provided by claim-pilot-logging package.
"""

__version__ = "2026.05.2"

# Re-export logging from claim-pilot-logging for convenience
from claim_pilot_logging import LogContext, get_logger, setup_logging

from .core import get_settings
from .database import DatabaseConnection, get_db

__all__ = [
    "__version__",
    "get_settings",
    "get_logger",
    "setup_logging",
    "LogContext",
    "get_db",
    "DatabaseConnection",
]
