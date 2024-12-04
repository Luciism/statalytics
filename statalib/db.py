import functools
import sqlite3

from .cfg import config


db_connect = lambda: sqlite3.connect(config.DB_FILE_PATH)
"Open a database connection."


def ensure_cursor(func):
    """
    Decorator to ensure a database cursor is resolved.

    If the `cursor` argument is `None`, a new db connection and cursor
    will be acquired, otherwise the passed `cursor` argument will be used.
    """
    @functools.wraps(func)
    async def wrapper(*args, **kwargs):
        cursor = kwargs.get('cursor')
        if cursor:  # Use provided cursor.
            return func(*args, **kwargs)

        # Create a new db connection and cursor object.
        with db_connect() as conn:
            cursor = conn.cursor()
            kwargs['cursor'] = cursor
            return func(*args, **kwargs)

    return wrapper
