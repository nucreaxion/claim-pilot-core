"""
Claim Pilot Core - Exception Hierarchy

Custom exceptions for insurance operations.
All exceptions inherit from ClaimPilotError for easy catching.
"""

from typing import Any, Dict, Optional


class ClaimPilotError(Exception):
    """
    Base exception for all Claim Pilot errors.

    Attributes:
        message: Human-readable error message
        code: Machine-readable error code
        details: Additional context about the error
        cause: Original exception if wrapping another error
    """

    def __init__(
        self,
        message: str,
        code: str = "CLAIM_PILOT_ERROR",
        details: Optional[Dict[str, Any]] = None,
        cause: Optional[Exception] = None,
    ):
        super().__init__(message)
        self.message = message
        self.code = code
        self.details = details or {}
        self.cause = cause

    def to_dict(self) -> Dict[str, Any]:
        return {"error": self.code, "message": self.message, "details": self.details}


# Database errors
class DatabaseError(ClaimPilotError):
    def __init__(self, message: str = "Database operation failed", details: Optional[Dict[str, Any]] = None, cause: Optional[Exception] = None):
        super().__init__(message=message, code="DATABASE_ERROR", details=details, cause=cause)


class ConnectionError(DatabaseError):
    def __init__(self, message: str = "Failed to connect to database", details: Optional[Dict[str, Any]] = None, cause: Optional[Exception] = None):
        super().__init__(message=message, details=details, cause=cause)
        self.code = "DATABASE_CONNECTION_ERROR"


# Tool errors
class ToolExecutionError(ClaimPilotError):
    def __init__(self, tool_name: str, message: str = "Tool execution failed", details: Optional[Dict[str, Any]] = None, cause: Optional[Exception] = None):
        super().__init__(message=f"{tool_name}: {message}", code="TOOL_EXECUTION_ERROR", details={"tool": tool_name, **(details or {})}, cause=cause)
        self.tool_name = tool_name


# Validation errors
class ValidationError(ClaimPilotError):
    def __init__(self, message: str = "Validation failed", field: Optional[str] = None, details: Optional[Dict[str, Any]] = None):
        super().__init__(message=message, code="VALIDATION_ERROR", details={"field": field, **(details or {})} if field else details)
        self.field = field


# Not found errors
class NotFoundError(ClaimPilotError):
    def __init__(self, resource_type: str, resource_id: str, message: Optional[str] = None):
        super().__init__(message=message or f"{resource_type} not found: {resource_id}", code="NOT_FOUND", details={"resource_type": resource_type, "resource_id": resource_id})
        self.resource_type = resource_type
        self.resource_id = resource_id


class PolicyNotFoundError(NotFoundError):
    def __init__(self, policy_id: str):
        super().__init__(resource_type="Policy", resource_id=policy_id)
        self.code = "POLICY_NOT_FOUND"


class ClaimNotFoundError(NotFoundError):
    def __init__(self, claim_id: str):
        super().__init__(resource_type="Claim", resource_id=claim_id)
        self.code = "CLAIM_NOT_FOUND"


# Authorization errors
class AuthorizationError(ClaimPilotError):
    def __init__(self, message: str = "Not authorized", details: Optional[Dict[str, Any]] = None):
        super().__init__(message=message, code="AUTHORIZATION_ERROR", details=details)
