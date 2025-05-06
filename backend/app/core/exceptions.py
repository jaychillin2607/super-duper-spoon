from fastapi import status
from typing import Optional, Dict, Any


class BaseAppException(Exception):
    """Base exception class for application errors"""

    def __init__(
        self,
        message: str = "An unexpected error occurred",
        status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR,
        details: Optional[Dict[str, Any]] = None,
    ):
        self.message = message
        self.status_code = status_code
        self.details = details or {}
        super().__init__(self.message)


class DatabaseError(BaseAppException):
    """Exception for database-related errors"""

    def __init__(
        self,
        message: str = "Database operation failed",
        details: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(
            message=message,
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            details=details,
        )


class DuplicateEntryError(BaseAppException):
    """Exception for duplicate entry errors"""

    def __init__(
        self,
        message: str = "A duplicate entry was detected",
        details: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(
            message=message, status_code=status.HTTP_409_CONFLICT, details=details
        )


class SessionError(BaseAppException):
    """Exception for session-related errors"""

    def __init__(
        self,
        message: str = "Session operation failed",
        details: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(
            message=message,
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            details=details,
        )


class SessionNotFoundError(SessionError):
    """Exception for session not found errors"""

    def __init__(
        self,
        message: str = "Session not found or expired",
        details: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(message=message, details=details)
        self.status_code = status.HTTP_404_NOT_FOUND


class ValidationError(BaseAppException):
    """Exception for validation errors"""

    def __init__(
        self,
        message: str = "Validation error",
        details: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(
            message=message, status_code=status.HTTP_400_BAD_REQUEST, details=details
        )


class EnrichmentError(BaseAppException):
    """Exception for enrichment API errors"""

    def __init__(
        self,
        message: str = "Enrichment service error",
        details: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(
            message=message, status_code=status.HTTP_502_BAD_GATEWAY, details=details
        )


class IncompleteFormError(BaseAppException):
    """Exception for incomplete form submission"""

    def __init__(
        self,
        message: str = "Form data is incomplete",
        details: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(
            message=message, status_code=status.HTTP_400_BAD_REQUEST, details=details
        )
