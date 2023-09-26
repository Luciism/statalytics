import logging

from .handlers import CustomTimedRotatingFileHandler


def setup_logging():
    """Setup logging handlers"""
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO)
    root_logger.addHandler(CustomTimedRotatingFileHandler())

