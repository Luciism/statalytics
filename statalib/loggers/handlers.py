"""Logging handlers."""

import os
import time
from logging.handlers import TimedRotatingFileHandler

from .formatters import UncoloredFormatter


class CustomTimedRotatingFileHandler(TimedRotatingFileHandler):
    """Custom file handler that uses a custom backup format."""
    def __init__(
        self,
        filename='latest.log',
        backup_format='%Y-%m-%d',
        logs_dir='logs/',
        when='d',
        interval=1,
        backupCount=0,
        encoding='utf-8',
        delay=False,
        utc=False,
        atTime=None,
        errors=None,
        formatter=UncoloredFormatter
    ) -> None:
        """
        Initialize the handler.

        :param filename: The name of the latest log file.
        :param backup_format: The date format to use for the backup files.
        :param logs_dir: The directory to store the logs in.
        :param when: The frequency to rotate the logs.
        :param interval: The interval to rotate the logs.
        :param backupCount: The number of backup files to keep.
        :param encoding: The encoding to use for the log file.
        :param delay: Whether to delay the creation of the file.
        :param utc: Whether to use UTC time.
        :param atTime: The time to rotate the logs.
        :param errors: The error level to log to the file.
        :param formatter: The formatter to use for the log file.
        """
        self.backup_format = backup_format
        self.logs_dir = logs_dir

        if not os.path.exists(logs_dir):
            os.makedirs(logs_dir)

        filename = f'{logs_dir}/{filename}'

        super().__init__(
            filename, when, interval, backupCount,
            encoding, delay, utc, atTime, errors
        )
        self.setFormatter(formatter)


    def rotation_filename(self, default_name) -> str:
        """Modify the filename of a log file when rotating."""
        backup_format = time.strftime(self.backup_format)
        backup_format = backup_format.removesuffix('.log')

        base_filename = os.path.join(self.logs_dir, backup_format)

        # construct a new filename based on the current time
        i = 1
        suffix = f'_{i}'

        while os.path.exists(f'{base_filename}{suffix}.log'):
            suffix = f'_{i}'
            i += 1

        return f'{base_filename}{suffix}.log'
