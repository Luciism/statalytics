"""A handful of useful loose functions."""

import asyncio
import functools
import typing
from datetime import UTC, datetime
from typing import ParamSpec, TypeVar, Callable, Coroutine, Any

P = ParamSpec("P")
T = TypeVar("T")


def to_thread(
    func: typing.Callable[P, T],
) -> Callable[P, Coroutine[typing.Any, typing.Any, T]]:
    """Converts a function to run on a separate thread."""

    @functools.wraps(func)
    async def wrapper(*args: P.args, **kwargs: P.kwargs) -> T:
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
