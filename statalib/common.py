import os
from datetime import datetime, UTC


REL_PATH = os.path.abspath(f'{__file__}/../..')
"The base path of the project."


class _MissingSentinel:  # Thanks discord.py
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

utc_now = lambda: datetime.now(UTC)
