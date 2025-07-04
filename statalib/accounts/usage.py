"""Account usage related functionality."""

from ..db import ensure_cursor, Cursor


class AccountUsage:
    """A usage manager for the account."""
    def __init__(self, discord_user_id: int) -> None:
        self._discord_user_id = discord_user_id

    @ensure_cursor
    def get_commands_ran(
        self,
        command_id: str | None=None,
        *, cursor: Cursor=None
    ) -> int:
        """
        Get the total or command specific number of commands ran by the user.

        :param command_id: The ID of the command to get the usage for. If left as \
            `None`, it will return the total number of commands ran by the user.
        :return int: The number of commands ran by the user.
        """
        if command_id is None:
            command_id = 'overall'

        result = cursor.execute(
            f'SELECT {command_id} FROM command_usage WHERE discord_id = ?',
            (self._discord_user_id,),
        ).fetchone()

        if result:
            return result[0]
        return 0

    @ensure_cursor
    def delete_all_usage_data(self, *, cursor: Cursor=None) -> None:
        """
        Irreversibly delete all the user's usage data.
        """
        cursor.execute(
            'DELETE FROM command_usage WHERE discord_id = ?',
            (self._discord_user_id,))

