"""A handful of useful loose functions."""

import typing
import asyncio
import functools
from datetime import datetime, UTC


def to_thread(func: typing.Callable) -> typing.Coroutine:
    """Converts a function to run on a separate thread."""
    @functools.wraps(func)
    async def wrapper(*args, **kwargs):
        return await asyncio.to_thread(func, *args, **kwargs)
    return wrapper


# I don't have a fucking clue mate.
def timezone_relative_timestamp(timestamp: int | float):
    """
    Adds local time difference to a UTC timestamp.

    :param timestamp: The timestamp to modify.
    """
    now_timestamp = datetime.now().timestamp()
    utcnow_timestamp = datetime.now(UTC).timestamp()

    timezone_difference = now_timestamp - utcnow_timestamp

    return timestamp + timezone_difference
