from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
from sqlalchemy.exc import SQLAlchemyError
import redis.exceptions
import json
import time
import uuid
from typing import Callable
import traceback

from app.core.config import get_settings
from app.core.logging import setup_logging, get_logger
from app.api.routes import session, enrichment, leads
from app.core.exceptions import BaseAppException
from app.core.exception_handlers import (
    app_exception_handler,
    sqlalchemy_exception_handler,
    redis_exception_handler,
    validation_exception_handler,
    json_exception_handler,
    generic_exception_handler,
)


setup_logging()
logger = get_logger(__name__)

settings = get_settings()
logger.info(f"Starting {settings.APP_NAME} v{settings.APP_VERSION}")


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="API for merchant lead form with session persistence and enrichment",
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # For demo purposes - restrict in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.add_exception_handler(BaseAppException, app_exception_handler)
app.add_exception_handler(SQLAlchemyError, sqlalchemy_exception_handler)
app.add_exception_handler(redis.exceptions.RedisError, redis_exception_handler)
app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.add_exception_handler(json.JSONDecodeError, json_exception_handler)
app.add_exception_handler(Exception, generic_exception_handler)


app.include_router(session.router)
app.include_router(enrichment.router)
app.include_router(leads.router)


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    logger.debug("Health check requested")
    return {"status": "ok", "version": settings.APP_VERSION}


@app.middleware("http")
async def logging_middleware(request: Request, call_next: Callable):
    """Middleware for request logging and timing"""
    # Generate a unique request ID
    request_id = request.headers.get("X-Request-ID", str(uuid.uuid4()))

    # Configure logging with request ID
    setup_logging(request_id)
    request_logger = get_logger("app.request")

    # Extract client info
    client_host = request.client.host if request.client else "unknown"
    user_agent = request.headers.get("User-Agent", "unknown")

    # Log the request
    request_logger.info(
        f"Request started: {request.method} {request.url.path}",
        extra={
            "method": request.method,
            "path": request.url.path,
            "query_params": str(request.query_params),
            "client_ip": client_host,
            "user_agent": user_agent,
            "request_id": request_id,
        },
    )

    # Time the request
    start_time = time.time()

    try:
        # Process the request
        response = await call_next(request)

        # Calculate request duration
        duration = time.time() - start_time

        # Add request ID header to response
        response.headers["X-Request-ID"] = request_id

        # Log the response
        request_logger.info(
            f"Request completed: {response.status_code} in {duration:.4f}s",
            extra={
                "status_code": response.status_code,
                "duration": duration,
                "request_id": request_id,
            },
        )

        return response

    except Exception as e:
        # Calculate request duration
        duration = time.time() - start_time

        # Log the exception
        request_logger.error(
            f"Request failed: {str(e)}",
            extra={
                "error": str(e),
                "error_type": type(e).__name__,
                "traceback": traceback.format_exc(),
                "duration": duration,
                "request_id": request_id,
            },
        )

        # Re-raise the exception to be handled by exception handlers
        raise


@app.on_event("startup")
async def startup_event():
    """Execute code on application startup"""
    logger.info("Application startup")

    # Log application configuration (excluding sensitive values)
    safe_settings = {
        "APP_NAME": settings.APP_NAME,
        "APP_VERSION": settings.APP_VERSION,
        "DEBUG": settings.DEBUG,
        "LOG_LEVEL": settings.LOG_LEVEL,
        "LOG_FORMAT": settings.LOG_FORMAT,
        # Exclude database connection strings and other sensitive data
    }
    logger.info(f"Application settings: {safe_settings}")


@app.on_event("shutdown")
async def shutdown_event():
    """Execute code on application shutdown"""
    logger.info("Application shutdown")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
