from fastapi import Request, status
from fastapi.responses import JSONResponse
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
import logging
import json

from app.core.exceptions import BaseAppException

logger = logging.getLogger(__name__)


async def app_exception_handler(
    request: Request, exc: BaseAppException
) -> JSONResponse:
    """
    Handler for custom application exceptions

    Args:
        request: FastAPI request object
        exc: BaseAppException or subclass

    Returns:
        JSON response with error details
    """
    logger.error(
        f"Application exception: {exc.message}",
        extra={"path": request.url.path, "details": exc.details},
    )

    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": exc.message,
            "details": exc.details,
            "type": exc.__class__.__name__,
        },
    )


async def sqlalchemy_exception_handler(
    request: Request, exc: SQLAlchemyError
) -> JSONResponse:
    """
    Handler for SQLAlchemy exceptions

    Args:
        request: FastAPI request object
        exc: SQLAlchemy exception

    Returns:
        JSON response with error details
    """
    logger.error(
        f"Database error: {str(exc)}", extra={"path": request.url.path}, exc_info=True
    )

    # Handle specific database errors
    if isinstance(exc, IntegrityError):
        if "uq_lead_email_business" in str(exc):
            return JSONResponse(
                status_code=status.HTTP_409_CONFLICT,
                content={
                    "error": "An application for this business with this email already exists.",
                    "type": "DuplicateEntryError",
                },
            )

        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={
                "error": "Database constraint violation.",
                "type": "IntegrityError",
            },
        )

    # Generic database error
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"error": "A database error occurred.", "type": "DatabaseError"},
    )


async def redis_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """
    Handler for Redis exceptions

    Args:
        request: FastAPI request object
        exc: Redis exception

    Returns:
        JSON response with error details
    """
    logger.error(
        f"Redis error: {str(exc)}", extra={"path": request.url.path}, exc_info=True
    )

    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"error": "Session storage error.", "type": "SessionError"},
    )


async def validation_exception_handler(
    request: Request, exc: Exception
) -> JSONResponse:
    """
    Handler for validation exceptions

    Args:
        request: FastAPI request object
        exc: Validation exception

    Returns:
        JSON response with error details
    """
    logger.error(f"Validation error: {str(exc)}", extra={"path": request.url.path})

    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={
            "error": "Validation error.",
            "details": str(exc),
            "type": "ValidationError",
        },
    )


async def json_exception_handler(
    request: Request, exc: json.JSONDecodeError
) -> JSONResponse:
    """
    Handler for JSON decode errors

    Args:
        request: FastAPI request object
        exc: JSON decode exception

    Returns:
        JSON response with error details
    """
    logger.error(f"JSON decode error: {str(exc)}", extra={"path": request.url.path})

    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={"error": "Invalid JSON format.", "type": "JSONDecodeError"},
    )


async def generic_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """
    Handler for generic exceptions

    Args:
        request: FastAPI request object
        exc: Any exception

    Returns:
        JSON response with error details
    """
    logger.error(
        f"Unhandled exception: {str(exc)}",
        extra={"path": request.url.path},
        exc_info=True,
    )

    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"error": "An unexpected error occurred.", "type": "ServerError"},
    )
