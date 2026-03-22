"""Logging utilities for setting up logging."""

import logging

from .handlers import CustomTimedRotatingFileHandler
from ..cfg import config


def setup_logging(logs_dir: str="logs/"):
    """Setup logging handlers"""
    root_logger = logging.getLogger()
    root_logger.setLevel(config("logging.level"))
    root_logger.addHandler(CustomTimedRotatingFileHandler(logs_dir=logs_dir))
