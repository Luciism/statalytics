"""Account usage related functionality."""

from ..db import ensure_cursor, Cursor


class AccountUsage:
    """A usage manager for the account."""
    def __init__(self, discord_user_id: int) -> None:
        self._discord_user_id: int = discord_user_id

    @ensure_cursor
    def delete_all_usage_data(self, *, cursor: Cursor=None) -> None:
        """
        Irreversibly delete all the user's usage data.
        """
        _ = cursor.execute(
            'DELETE FROM command_metrics WHERE discord_id = ?',
            (self._discord_user_id,))

