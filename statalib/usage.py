"""Usage metrics related functionality."""

import time
from datetime import datetime, UTC
from typing import Literal, TypedDict

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
        timestamp = datetime.now(UTC).timestamp()

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


@ensure_cursor
def get_growth_difference(
    seconds: int,
    metric: Literal['guild', 'user', 'linked'],
    *, cursor: Cursor=None
) -> int:
    """
    Get the difference in a growth metric from the last `seconds` seconds.

    :param seconds: The number of seconds to get the difference from.
    :param metric: The metric to get the difference from.
    :return int: The difference in the metric.
    """
    since = datetime.now(UTC).timestamp() - seconds

    growth_data = cursor.execute(
        'SELECT action FROM growth_data '
        'WHERE growth = ? and timestamp > ? '
        'ORDER BY timestamp DESC',
        (metric, since)
    ).fetchall()

    # Calculate the difference based on the type of entry
    diff = 0
    for grow in growth_data:
        if grow[0] == 'add':
            diff += 1
        else:
            diff -= 1

    return diff


class TimestampsSinceDict(TypedDict):
    timestamp: float
    action: str


class Metrics:
    def __init__(self, metric: Literal['guild', 'user', 'linked']) -> None:
        self.metric = metric

    @ensure_cursor
    def get_timestamps_since(
        self, seconds_ago: int, *, cursor: Cursor=None
    ) -> list[TimestampsSinceDict]:
        timestamp = datetime.now(UTC).timestamp() - seconds_ago

        results = cursor.execute(
            'SELECT timestamp, action FROM growth_data '
            'WHERE growth = ? and timestamp > ? '
            'ORDER BY timestamp DESC',
            (self.metric, timestamp)
        ).fetchall()

        return [{'timestamp': row[0], 'action': row[1]} for row in results]


    def group_timestamps(
        self,
        timestamps_1: list[float],
        timestamps_2: list[float] | None=None,
        date_format: str="%b %d, %Y"
    ) -> tuple[list[str], list[float]] | tuple[list[str], list[float], list[float]]:
        grouped_data: dict[str, dict[str, int]] = {}

        # Create a datetime object for each timestamp
        datetimes_1 = [datetime.fromtimestamp(ts, UTC) for ts in timestamps_1]
        all_datetimes = sorted(datetimes_1)

        # Do the same for timestamps 2 if it is passed
        if timestamps_2 is not None:
            datetimes_2 = [datetime.fromtimestamp(ts, UTC) for ts in timestamps_2]
            all_datetimes.extend(datetimes_2)
            all_datetimes.sort()

        # Group the timestamps by day
        for dt in all_datetimes:
            # Round the timestamp to the nearest 24 hours
            day_dt = dt.replace(
                hour=(dt.hour // 24) * 24, minute=0, second=0, microsecond=0)

            date_str = day_dt.strftime(date_format)
            grouped_data.setdefault(date_str, {'1': 0, '2': 0})

            # Increment the count for the day
            if dt in datetimes_1:
                grouped_data[date_str]['1'] += 1

            if timestamps_2 is not None and dt in datetimes_2:
                grouped_data[date_str]['2'] += 1

        # Return the grouped data
        formatted_timestamps = list(grouped_data.keys())
        data_count_1 = [grouped_data[key]['1'] for key in grouped_data]

        if datetimes_2 is None:
            return formatted_timestamps, data_count_1

        data_count_2 = [grouped_data[key]['2'] for key in grouped_data]
        return formatted_timestamps, data_count_1, data_count_2
