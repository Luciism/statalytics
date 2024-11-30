"""Logging utilities for setting up logging."""

import logging

from .handlers import CustomTimedRotatingFileHandler


def setup_logging(logs_dir: str="logs/"):
    """Setup logging handlers"""
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO)
    root_logger.addHandler(CustomTimedRotatingFileHandler(logs_dir=logs_dir))
