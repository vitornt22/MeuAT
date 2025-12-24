import logging
import json
import sys
from datetime import datetime


class StructuredFormatter(logging.Formatter):
    """Formatter that transforms log records into a structured JSON object."""

    def format(self, record):
        # Construct the log dictionary with essential metadata
        log_record = {
            "timestamp": datetime.utcnow().isoformat(),
            "level": record.levelname,
            "message": record.getMessage(),
            "module": record.module,
            "funcName": record.funcName,
        }

        # Include stack trace if an exception is present
        if record.exc_info:
            log_record["exception"] = self.formatException(record.exc_info)

        return json.dumps(log_record)


def setup_logging():
    """Initializes global logging configuration with a JSON structured output."""

    # Configure handler to output to standard stream (stdout)
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(StructuredFormatter())

    # Configure root logger level and attach the custom handler
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO)
    root_logger.addHandler(handler)

    # Remove pre-existing default handlers to prevent duplicate logs
    # (Commonly needed when running under Uvicorn or Gunicorn)
    for h in root_logger.handlers[:-1]:
        root_logger.removeHandler(h)
