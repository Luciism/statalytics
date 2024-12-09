"""Common constants and functions."""

import os
from datetime import datetime, UTC


REL_PATH = os.path.abspath(f'{__file__}/../..')
"The base path of the project."

class _MissingSentinel:  # Thanks discord.py
    """A sentinel object to represent the absence of a value."""
    __slots__ = ()
    def __eq__(self, other) -> bool:
        return False
    def __bool__(self) -> bool:
        return False
    def __hash__(self) -> int:
        return 0
    def __repr__(self):
        return '...'

MISSING = _MissingSentinel()
"Global missing sentinel instance."

def utc_now() -> datetime:
    """Get the current UTC datetime."""
    return datetime.now(UTC)
