"""A handful of useful loose functions."""

import json
import time
import random
import typing
import sqlite3
import asyncio
import functools
from typing import Literal, Any
from datetime import datetime, timedelta, UTC

import discord

from .cfg import config
from .common import REL_PATH


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


def to_thread(func: typing.Callable) -> typing.Coroutine:
    """Converts a function to run on a separate thread."""
    @functools.wraps(func)
    async def wrapper(*args, **kwargs):
        return await asyncio.to_thread(func, *args, **kwargs)
    return wrapper


def get_embed_color(embed_type: Literal["primary", "warning", "danger"]) -> int:
    """
    Get a base 16 integer for a specfied embed color.

    :param embed_type: The embed color type (primary, warning, or danger).
    """
    return int(config(f'apps.bot.embeds.{embed_type}_color'), base=16)


def loading_message() -> str:
    """Get the currently configured loading message."""
    return config('apps.bot.loading_message')


def insert_growth_data(
    discord_id: int,
    action: Literal['add', 'remove'],
    growth: Literal['guild', 'user', 'linked'],
    timestamp: float=None
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

    with db_connect() as conn:
        cursor = conn.cursor()

        cursor.execute(
            'INSERT INTO growth_data '
            '(timestamp, discord_id, action, growth) '
            'VALUES (?, ?, ?, ?)',
            (timestamp, discord_id, action, growth)
        )


def _update_usage(command, discord_id):
    with db_connect() as conn:
        cursor = conn.cursor()

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
        insert_growth_data(discord_id, action='add', growth='user')


def update_command_stats(discord_id: int, command: str) -> None:
    """
    Updates command usage stats for respective command.

    :param discord_id: The Discord ID of the user that ran the command.
    :param command: The ID of the command run by the user to be incremented.
    """
    _update_usage(command, discord_id)
    _update_usage(command, 0)  # Global commands


def fname(username: str):
    """Escapes underscore characters to bypass Discord's markdown."""
    return username.replace("_", "\_")


def ordinal(n: int) -> str:
    """
    Formats a day of the month, for example `21` would be `21st`.

    :param n: The number to format.
    """
    if 4 <= n % 100 <= 20:
        return "th"
    return {1: "st", 2: "nd", 3: "rd"}.get(n % 10, "th")


def get_user_total() -> int:
    """Get total amount of account that exist."""
    with db_connect() as conn:
        cursor = conn.cursor()

        cursor.execute('SELECT COUNT(account_id) FROM accounts')
        result = cursor.fetchone()

    if result:
        return result[0]
    return 0


def _commands_ran(discord_id: int, default: Any, cursor: sqlite3.Cursor):
    cursor.execute(
        'SELECT overall FROM command_usage WHERE discord_id = ?', (discord_id,))
    result = cursor.fetchone()

    if result:
        return result[0]
    return default


def commands_ran(
    discord_id: int,
    default: Any=0,
    cursor: sqlite3.Cursor=None
) -> int | Any:
    """
    Get the total amount of commands that a user has ran.

    :param discord_id: The Discord user ID of the respective user.
    :param default: The default return value if the user has never run a command.
    :param cursor: A custom `sqlite3.Cursor` object to operate on.
    """
    if cursor:
        return _commands_ran(discord_id, default, cursor)

    with db_connect() as conn:
        cursor = conn.cursor()
        return _commands_ran(discord_id, default, cursor)


def get_commands_total() -> int:
    """Get the total amount of commands run by all users, ever."""
    with db_connect() as conn:
        cursor = conn.cursor()

        cursor.execute('SELECT overall FROM command_usage WHERE discord_id = 0')
        result = cursor.fetchone()

    if result:
        return result[0]
    return 0


def _set_embed_color(embed: discord.Embed, color: str | int):
    if color is not None:
        embed.color = color if isinstance(color, int) else get_embed_color(color)
    return embed


def __format_embed_fields(
    embed_json: dict,
    prop_values: dict[int, dict[str, dict[str, str]]]
) -> None:
    # loop over each field to format
    for field_index, field in prop_values.items():
        # get the embed field currently being targeted
        target_field: dict[str, str] = embed_json['fields'][field_index]

        for field_prop_name, field_prop_values in field.items():
            # format the property of the target field
            target_field[field_prop_name] = \
                target_field[field_prop_name].format(**field_prop_values)


def load_embeds(
    filename: str,
    format_values: dict[str, dict[str, str] | list[dict[str, dict[str, str]]]]=None,
    color: int | Literal['primary', 'warning', 'danger']=None
) -> list[discord.Embed]:
    """
    Loads a list of embeds from a json file.

    Example:
    ```python
    load_embeds(
        filename='example',
        format_values={
            'title': {
                'some_format_key': 'some_format_value'
            },
            'description': {
                'example': 'value',
                'hello': 'world'
            },
            'fields': {
                0: {
                    'name': {
                        'foo': 'bar'
                    }
                }
                2: {
                    'value': {
                        'foo': 'bar'
                    }
                }
            }
        }
    )
    ```
    :param filename: The name of the file containing the embed json data\
        (.json ext optional).
    :param format_values: A list of format values respective to their properties.
    :param color: Override embed color, can be integer directly or 'primary',\
        'warning', 'danger'.
    """
    if not filename.endswith('.json'):
        filename += '.json'

    # Load embed data
    with open(f"{REL_PATH}/assets/embeds/{filename}") as df:
        embed_dict = json.load(df)

    embeds = []

    # loop over actual embeds
    for embed_json in embed_dict['embeds']:
        if format_values is not None:
            # the property to format (eg: description)
            for prop_name, prop_values in format_values.items():
                # if the property is a list of fields,
                # format every field to use the format values
                if prop_name == 'fields':
                    __format_embed_fields(embed_json, prop_values)
                else:
                    embed_json[prop_name] = embed_json[prop_name].format(**prop_values)

        # load Embed item from embed json dict and set color
        embed = discord.Embed.from_dict(embed_json)
        embeds.append(_set_embed_color(embed, color))

    return embeds


# Why does this exist?
def get_timestamp(blacklist: tuple[float]=None) -> int:
    """
    Return the the first current timestamp that is not
    in a list of blacklisted timestamps.

    :param blacklist: A blacklisted list of timestamps.
    """
    timestamp = datetime.now(UTC).timestamp()

    if blacklist:
        i = 0
        while timestamp in blacklist:
            extra = random.randint(1, 100) / 10000
            timestamp += extra
            i += extra

    return timestamp


async def align_to_hour():
    """Sleep until the next hour."""
    now = datetime.now()
    sleep_seconds = (60 - now.minute) * 60 - now.second
    await asyncio.sleep(sleep_seconds)


def int_prefix(integer: int | float) -> str:
    """
    Returns a prefix (+, -) for an integer depending on whether it is
    positive or negative respectively. If the number is a negative number,
    an empty string will be returned as a `-` is already present.

    :param integer: The integer to determine the prefix of.
    """
    if integer >= 0:
        return "+"
    return ""


def prefix_int(integer: int | float) -> str:
    """
    Prefixes a given number with `+` or `-` and returns it as a string.

    :param integer: The integer to be prefixed.
    """
    return f'{int_prefix(integer)}{integer:,}'


def format_seconds(seconds):
    """
    Format a duration of seconds into a string such as `36 Mins`,
    `48 Hours`, or `12 Days`.

    :param seconds: The duration in seconds to format.
    """
    delta = timedelta(seconds=round(seconds))
    days = delta.days

    if days > 0:
        return f"{days} Day{'s' if days > 1 else ''}"

    hours = delta.seconds // 3600
    if hours > 0:
        return f"{hours} Hour{'s' if hours > 1 else ''}"

    minutes = (delta.seconds // 60) % 60
    return f"{minutes} Min{'s' if minutes > 1 else ''}"


def pluralize(number: int, word: str, suffix: str='s') -> str:
    """
    Pluralizes a word based on a given number.

    :param number: The number to determine whether to pluralize.
    :param word: The word to pluralize.
    :param suffix: The plural suffix to add to the word.
    """
    if number != 1:
        return f'{word}{suffix}'
    return word


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


def comma_separated_to_list(comma_seperated_list: str) -> list:
    """
    Converts a comma seperated list (string) to a list of strings.
    Example `"foo,bar"` -> `["foo", "bar"]`.

    :param comma_seperated_list: The comma seperated list of items.
    """
    if comma_seperated_list:
        return comma_seperated_list.split(',')
    return []


def setup_database_schema(
    schema_fp=f"{REL_PATH}/schema.sql",
    db_fp=config.DB_FILE_PATH
) -> None:
    """
    Run the database schema setup script.

    :param schema_fp: The path to the database schema setup script.
    :param db_fp: The path to the database file.
    """
    with open(schema_fp) as db_schema_file:
        db_schema_setup = db_schema_file.read()

    with sqlite3.connect(db_fp) as conn:
        cursor = conn.cursor()
        cursor.executescript(db_schema_setup)


def format_12hr_time(hour: int, minute: int) -> str:
  """Format time as hr:min(AM/PM)"""
  hour_12 = hour % 12
  hour_12 = 12 if hour_12 == 0 else hour_12

  period = "AM" if hour < 12 else "PM"
  return f"{hour_12}:{minute:02d}{period}"
