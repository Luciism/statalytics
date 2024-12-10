"""Usage metrics related functionality."""

import time
from typing import Literal

from .db import ensure_cursor, Cursor


@ensure_cursor
def insert_growth_data(
    discord_id: int,
    action: Literal['add', 'remove'],
    growth: Literal['guild', 'user', 'linked'],
    timestamp: float=None,
    *, cursor: Cursor=None
) -> None:
    """
    Inserts a row of growth data into database.

    :param discord_id: The respective Discord ID of the event (guild, user, etc).
    :param action: The action that affected the growth (add, remove, etc).
    :param growth: The growth metric that was impacted (guild, user, etc).
    :param timestamp: The timestamp of the growth (defaults to now).
    """
    if timestamp is None:
        timestamp = time.time()

    cursor.execute(
        'INSERT INTO growth_data '
        '(timestamp, discord_id, action, growth) '
        'VALUES (?, ?, ?, ?)',
        (timestamp, discord_id, action, growth)
    )


def _update_usage(command, discord_id, cursor: Cursor) -> None:
    # Check if command column exists
    cursor.execute('SELECT * FROM command_usage WHERE discord_id = 0')
    column_names = [desc[0] for desc in cursor.description]

    # Add column if it doesnt exist
    if not command in column_names:
        cursor.execute(f'ALTER TABLE command_usage ADD COLUMN {command} INTEGER')

    # Update users command usage stats
    cursor.execute(
        f"SELECT overall, {command} FROM command_usage WHERE discord_id = ?",
        (discord_id,))
    result = cursor.fetchone()

    if result and result[0]:
        cursor.execute(f"""
            UPDATE command_usage
            SET overall = overall + 1,
            {command} = {f'{command} + 1' if result[1] else 1}
            WHERE discord_id = {discord_id}
        """)  # if command current is null, it will be set to 1
    else:
        cursor.execute(
            "INSERT INTO command_usage "
            f"(discord_id, overall, {command}) VALUES (?, ?, ?)",
            (discord_id, 1, 1))

    if not result:
        insert_growth_data(discord_id, action='add', growth='user', cursor=cursor)


@ensure_cursor
def update_command_stats(
    discord_id: int, command: str, *, cursor: Cursor=None
) -> None:
    """
    Updates command usage stats for respective command.

    :param discord_id: The Discord ID of the user that ran the command.
    :param command: The ID of the command run by the user to be incremented.
    """
    _update_usage(command, discord_id, cursor=cursor)
    _update_usage(command, 0, cursor=cursor)  # Global commands


@ensure_cursor
def get_user_total(*, cursor: Cursor=None) -> int:
    """Get total amount of account that exist."""
    result = cursor.execute('SELECT COUNT(account_id) FROM accounts').fetchone()

    if result:
        return result[0]
    return 0


@ensure_cursor
def get_commands_total(*, cursor: Cursor=None) -> int:
    """Get the total amount of commands run by all users, ever."""
    cursor.execute('SELECT overall FROM command_usage WHERE discord_id = 0')
    result = cursor.fetchone()

    if result:
        return result[0]
    return 0
