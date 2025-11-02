"""Database related functionality."""

import functools
import sqlite3
import aiosqlite
from aiosqlite import Cursor as AsyncCursor
from sqlite3 import Cursor

from .common import REL_PATH
from .cfg import config


def db_connect() -> sqlite3.Connection:
    "Open a database connection."
    return sqlite3.connect(config.DB_FILE_PATH)


def ensure_cursor(func):
    """
    Decorator to ensure a database cursor is resolved.

    If the `cursor` argument is `None`, a new db connection and cursor
    will be acquired, otherwise the passed `cursor` argument will be used.
    """
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        cursor: Cursor | None = kwargs.get('cursor')
        if cursor:  # Use provided cursor.
            return func(*args, **kwargs)

        # Create a new db connection and cursor object.
        with db_connect() as conn:
            cursor = conn.cursor()
            kwargs['cursor'] = cursor
            return func(*args, **kwargs)

    return wrapper


def async_ensure_cursor(func):
    """
    *Uses aiosqlite*
    Decorator to ensure a database cursor is resolved.

    If the `cursor` argument is `None`, a new db connection and cursor
    will be acquired, otherwise the passed `cursor` argument will be used.
    Automatically commits the changes.
    """
    @functools.wraps(func)
    async def wrapper(*args, **kwargs):
        cursor: AsyncCursor | None = kwargs.get('cursor')
        if cursor:  # Use provided cursor.
            return await func(*args, **kwargs)

        # Create a new db connection and cursor object.
        async with aiosqlite.connect(config.DB_FILE_PATH) as conn:
            cursor = await conn.cursor()
            cursor.row_factory = aiosqlite.Row
            kwargs['cursor'] = cursor

            result = await func(*args, **kwargs)

            await conn.commit()

            return result

    return wrapper


def setup_database_schema(
    schema_fp: str=f"{REL_PATH}/schema.sql",
    db_fp: str=config.DB_FILE_PATH
) -> None:
    """
    Run the database schema setup script.

    :param schema_fp: The path to the database schema setup script.
    :param db_fp: The path to the database file.
    """
    with open(schema_fp, encoding="utf-8") as db_schema_file:
        db_schema_setup = db_schema_file.read()

    with sqlite3.connect(db_fp) as conn:
        cursor = conn.cursor()
        cursor.executescript(db_schema_setup)


__all__ = [
    'db_connect',
    'ensure_cursor',
    'Cursor',
]
