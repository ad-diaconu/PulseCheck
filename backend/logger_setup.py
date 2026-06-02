from logging.config import dictConfig
import logging
from pythonjsonlogger import jsonlogger
import os

ENVIRONMENT = os.getenv("ENVIRONMENT","local")

class CustomJsonFormatter(jsonlogger.JsonFormatter):
    def add_fields(self, log_record, record, message_dict):
        super(CustomJsonFormatter, self).add_fields(log_record, record, message_dict)
        # Add timesamps and standardized log levels for Cloud VMs (Datadog/AWS CloudWatch)
        if not log_record.get("timestamp"):
            log_record["timestamp"] = record.created
        if log_record.get('level'):
            log_record["level"] = log_record['level'].upper()
        else:
            log_record['level'] = record.levelname

# master config
LOGGING_CONFIG = {
    "version": 1,
    "disable_existing_loggers": False, # CRITICAL: This allows us to intercept Uvicorn's loggers
    "formatters": {
        "json": {
            "()": CustomJsonFormatter,
            "fmt": "%(timestamp)s %(level)s %(name)s %(message)s"
        },
        "standard": {
            "format": "%(asctime)s [%(levelname)s] %(name)s: %(message)s"
        }
    },
    "handlers": {
        "console": {
            # Switch formatter based on environment
            "formatter": "json" if ENVIRONMENT == "production" else "standard",
            "class": "logging.StreamHandler",
            "stream": "ext://sys.stdout",
        },
    },
    "loggers": {
        # 1. FastAPI Application Logger
        "fastapi_app": {"handlers": ["console"], "level": "INFO", "propagate": False},
        
        # 2. Uvicorn Base Logger
        "uvicorn": {"handlers": ["console"], "level": "INFO", "propagate": False},
        
        # 3. Uvicorn Error Logger
        "uvicorn.error": {"level": "INFO"},
        
        # 4. Uvicorn Access Logger (Logs every HTTP request)
        "uvicorn.access": {"handlers": ["console"], "level": "INFO", "propagate": False},
    },
}

def setup_logging():
    dictConfig(LOGGING_CONFIG)
    return logging.getLogger("pulsecheck_app")
