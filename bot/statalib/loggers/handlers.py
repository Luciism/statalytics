import os
import time

from logging.handlers import TimedRotatingFileHandler


class CustomTimedRotatingFileHandler(TimedRotatingFileHandler):
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
        errors=None
    ):
        self.backup_format = backup_format
        self.logs_dir = logs_dir

        filename = f'{logs_dir}/{filename}'

        super().__init__(
            filename, when, interval, backupCount,
            encoding, delay, utc, atTime, errors
        )


    def rotation_filename(self, default_name):
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
