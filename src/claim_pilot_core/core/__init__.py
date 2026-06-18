"""
Claim Pilot Core - Core Module

Configuration, exceptions, and logging re-exports.
"""

from claim_pilot_logging import (
    LogContext,
    bind_context,
    clear_context,
    get_logger,
    log_metric,
    setup_logging,
    timed,
)

from .config import (
    BaseSettings,
    clear_remote_config_cache,
    clear_secrets_cache,
    create_settings,
    get_config_value,
    get_remote_config,
    get_secret,
    get_settings,
    reload_settings,
)
from .exceptions import (
    ClaimPilotError,
    DatabaseError,
    NotFoundError,
    ToolExecutionError,
    ValidationError,
)

__all__ = [
    # Config
    "BaseSettings",
    "create_settings",
    "get_settings",
    "reload_settings",
    "get_remote_config",
    "get_config_value",
    "clear_remote_config_cache",
    "get_secret",
    "clear_secrets_cache",
    # Logging (from claim-pilot-logging)
    "get_logger",
    "setup_logging",
    "LogContext",
    "bind_context",
    "clear_context",
    "timed",
    "log_metric",
    # Exceptions
    "ClaimPilotError",
    "DatabaseError",
    "ToolExecutionError",
    "ValidationError",
    "NotFoundError",
]
