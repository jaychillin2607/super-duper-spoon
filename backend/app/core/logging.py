import json
import logging
import sys
from datetime import datetime
from logging.handlers import RotatingFileHandler, TimedRotatingFileHandler
from pathlib import Path
import uuid
from typing import Dict, Any, Optional

from app.core.config import get_settings

settings = get_settings()


logs_dir = Path("logs")
logs_dir.mkdir(exist_ok=True)


class RequestIdFilter(logging.Filter):
    """Filter that adds request_id to log records"""

    def __init__(self, request_id: Optional[str] = None):
        super().__init__()
        self.request_id = request_id or str(uuid.uuid4())

    def filter(self, record):
        record.request_id = getattr(record, "request_id", self.request_id)
        return True


class JsonFormatter(logging.Formatter):
    """Format logs as JSON objects"""

    def format(self, record: logging.LogRecord) -> str:
        """
        Format the log record as a JSON string

        Args:
            record: The log record to format

        Returns:
            JSON formatted log string
        """
        log_data = {
            "timestamp": datetime.utcfromtimestamp(record.created).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
            "request_id": getattr(record, "request_id", "no_request"),
        }

        # Include exception info if available
        if record.exc_info:
            log_data["exception"] = {
                "type": record.exc_info[0].__name__,
                "message": str(record.exc_info[1]),
                "traceback": self.formatException(record.exc_info),
            }

        # Include any extra attributes passed to the logger
        for key, value in record.__dict__.items():
            if key not in {
                "args",
                "asctime",
                "created",
                "exc_info",
                "exc_text",
                "filename",
                "funcName",
                "id",
                "levelname",
                "levelno",
                "lineno",
                "module",
                "msecs",
                "message",
                "msg",
                "name",
                "pathname",
                "process",
                "processName",
                "relativeCreated",
                "stack_info",
                "thread",
                "threadName",
                "request_id",  # Already handled above
            }:
                # Try to make the value JSON serializable
                try:
                    json.dumps({key: value})
                    log_data[key] = value
                except (TypeError, OverflowError):
                    log_data[key] = str(value)

        return json.dumps(log_data)


def get_console_handler() -> logging.Handler:
    """
    Create a console handler for logs

    Returns:
        Configured console handler
    """
    console_handler = logging.StreamHandler(sys.stdout)
    console_formatter = (
        JsonFormatter()
        if settings.LOG_FORMAT == "json"
        else logging.Formatter(
            "%(asctime)s - %(name)s - [%(levelname)s] - %(message)s - [request_id=%(request_id)s]"
        )
    )
    console_handler.setFormatter(console_formatter)
    return console_handler


def get_file_handler() -> logging.Handler:
    """
    Create a file handler for logs with rotation

    Returns:
        Configured file handler
    """
    # Determine log filename
    log_file = logs_dir / f"{settings.APP_NAME.lower().replace(' ', '_')}.log"

    # Choose rotation strategy based on settings
    if settings.LOG_ROTATION_TYPE == "size":
        file_handler = RotatingFileHandler(
            log_file,
            maxBytes=settings.LOG_ROTATION_SIZE,
            backupCount=settings.LOG_ROTATION_BACKUPS,
        )
    else:  # time-based rotation
        file_handler = TimedRotatingFileHandler(
            log_file,
            when=settings.LOG_ROTATION_WHEN,
            interval=settings.LOG_ROTATION_INTERVAL,
            backupCount=settings.LOG_ROTATION_BACKUPS,
        )

    file_formatter = (
        JsonFormatter()
        if settings.LOG_FORMAT == "json"
        else logging.Formatter(
            "%(asctime)s - %(name)s - [%(levelname)s] - %(message)s - [request_id=%(request_id)s]"
        )
    )
    file_handler.setFormatter(file_formatter)
    return file_handler


def setup_logging(request_id: Optional[str] = None) -> None:
    """
    Set up logging configuration

    Args:
        request_id: Optional request ID for correlation
    """
    # Get root logger
    root_logger = logging.getLogger()

    # Clear existing handlers
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)

    # Set log level from settings
    root_logger.setLevel(settings.LOG_LEVEL)

    # Add request ID filter to all logs
    request_filter = RequestIdFilter(request_id)
    root_logger.addFilter(request_filter)

    # Add console handler
    if settings.LOG_TO_CONSOLE:
        root_logger.addHandler(get_console_handler())

    # Add file handler
    if settings.LOG_TO_FILE:
        root_logger.addHandler(get_file_handler())

    # Disable propagation for some noisy loggers
    for logger_name in ["uvicorn", "uvicorn.access"]:
        logging.getLogger(logger_name).propagate = False

    # Configure SQLAlchemy logging
    if settings.LOG_SQL:
        logging.getLogger("sqlalchemy.engine").setLevel(logging.INFO)
    else:
        logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)

    # Configure Redis logging
    logging.getLogger("redis").setLevel(logging.WARNING)


def get_logger(name: str) -> logging.Logger:
    """
    Get a logger with the given name

    Args:
        name: Name of the logger

    Returns:
        Configured logger
    """
    return logging.getLogger(name)


class LoggerAdapter(logging.LoggerAdapter):
    """Adapter to add context to log messages"""

    def __init__(self, logger: logging.Logger, context: Dict[str, Any]):
        """
        Initialize the adapter

        Args:
            logger: Logger to adapt
            context: Context to add to log messages
        """
        super().__init__(logger, context)

    def process(self, msg, kwargs):
        # Add context to the extra field
        kwargs.setdefault("extra", {}).update(self.extra)
        return msg, kwargs


def get_context_logger(name: str, context: Dict[str, Any]) -> logging.LoggerAdapter:
    """
    Get a logger with context

    Args:
        name: Name of the logger
        context: Context to add to log messages

    Returns:
        Logger adapter with context
    """
    logger = get_logger(name)
    return LoggerAdapter(logger, context)
