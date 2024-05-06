"""A set of useful functions used throughout the bot"""

import json
import time
import random
import typing
import sqlite3
import asyncio
import functools
from typing import Literal, Any
from datetime import datetime, timedelta

import discord

from .assets import ASSET_LOADER
from .aliases import PlayerUUID
from .cfg import config
from .common import REL_PATH


def to_thread(func: typing.Callable) -> typing.Coroutine:
    @functools.wraps(func)
    async def wrapper(*args, **kwargs):
        return await asyncio.to_thread(func, *args, **kwargs)
    return wrapper


def get_embed_color(embed_type: str) -> int:
    """
    Returns a base 16 integer from a hex code.
    :param embed_type: the embed color type (primary, warning, danger)
    """
    return int(config(f'apps.bot.embeds.{embed_type}_color'), base=16)


def loading_message() -> str:
    """
    Returns loading message from the `config.json` file
    """
    return config('apps.bot.loading_message')


def _get_voting_data(discord_id: int, cursor: sqlite3.Cursor) -> tuple:
    cursor.execute(f'SELECT * FROM voting_data WHERE discord_id = {discord_id}')
    return cursor.fetchone()


def get_voting_data(discord_id: int, cursor: sqlite3.Cursor=None) -> tuple:
    """
    Returns a users voting data
    :param discord_id: The discord id of the user's voting data to be fetched
    :param cursor: custom `sqlite3.Cursor` object to execute queries with
    """
    if cursor:
        return _get_voting_data(discord_id, cursor)

    with sqlite3.connect(f'{REL_PATH}/database/core.db') as conn:
        cursor = conn.cursor()
        return _get_voting_data(discord_id, cursor)


def insert_growth_data(
    discord_id: int,
    action: Literal['add', 'remove'],
    growth: Literal['guild', 'user', 'linked'],
    timestamp: float=None
):
    """
    Inserts a row of growth data into database
    :param discord_id: the respective discord id of the event (guild, user, etc)
    :param action: the action that caused growth (add, remove, etc)
    :param growth: what impacted the growth (guild, user, etc)
    :param timestamp: the timestamp of the action (defaults to now)
    """
    if timestamp is None:
        timestamp = time.time()

    with sqlite3.connect(f'{REL_PATH}/database/core.db') as conn:
        cursor = conn.cursor()

        cursor.execute(
            'INSERT INTO growth_data '
            '(timestamp, discord_id, action, growth) '
            'VALUES (?, ?, ?, ?)',
            (timestamp, discord_id, action, growth)
        )


def _update_usage(command, discord_id):
    with sqlite3.connect(f'{REL_PATH}/database/core.db') as conn:
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
    :param discord_id: the user that ran he command
    :param command: the command run by the user to increment
    """
    _update_usage(command, discord_id)
    _update_usage(command, 0)  # Global commands


def fname(username: str):
    """
    Returns an escaped version of a username to avoid discord markdown
    """
    return username.replace("_", "\_")


def ordinal(n: int) -> str:
    """
    Formats a day for example `21` would be `21st`
    :param n: The number to format
    """
    if 4 <= n % 100 <= 20:
        return "th"
    return {1: "st", 2: "nd", 3: "rd"}.get(n % 10, "th")


def get_user_total() -> int:
    """Returns total amount of users to have run a command"""
    with sqlite3.connect(f'{REL_PATH}/database/core.db') as conn:
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
    Returns the total commands ran for a certain user
    :param discord_id: the discord id of the respective user
    :param default: the default value to return if the user has\
        never run any commands
    :param cursor: custom `sqlite3.Cursor` object to execute queries with
    """
    if cursor:
        return _commands_ran(discord_id, default, cursor)

    with sqlite3.connect(f'{REL_PATH}/database/core.db') as conn:
        cursor = conn.cursor()
        return _commands_ran(discord_id, default, cursor)


def get_commands_total() -> int:
    """
    Returns total amount of commands run by all users
    """
    with sqlite3.connect(f'{REL_PATH}/database/core.db') as conn:
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
):
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
    color: int | str=None
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
    :param filename: the name of the file containing the embed json data\
        (.json ext optional)
    :param format_values: a list of format values respective to their properties
    :param color: override embed color, can be integer directly or 'primary',\
        'warning', 'danger'
    """
    if not filename.endswith('.json'):
        filename += '.json'

    # Load embed data
    embed_dict = ASSET_LOADER.load_embed(filename)

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


def get_timestamp(blacklist: tuple[float]=None) -> int:
    """
    Returns a unique timestamp that is not in a list of timestamps
    :param blacklist: blacklisted list of timestamps
    :param timestamp_type: the type to return the timestamp as
    """
    timestamp = datetime.utcnow().timestamp()

    if blacklist:
        i = 0
        while timestamp in blacklist:
            extra = random.randint(1, 100) / 10000
            timestamp += extra
            i += extra

    return timestamp


async def align_to_hour():
    """Sleeps until the next hour"""
    now = datetime.now()
    sleep_seconds = (60 - now.minute) * 60 - now.second
    await asyncio.sleep(sleep_seconds)


def int_prefix(integer: int | float) -> str:
    """
    Returns prefix (+, -) for a provided integer
    if the provided integer is a negative number
    an empty string will be returned as a `-` is
    already present
    :param integer: the integer to return the prefix of
    """
    if integer >= 0:
        return "+"
    return ""


def prefix_int(integer: int | float):
    """
    Prefixes given number with `+` or `-` and returns it as a string
    :param integer: the integer to be prefixed
    """
    return f'{int_prefix(integer)}{integer:,}'


def format_seconds(seconds):
    """
    Formats an amount of seconds into a string for example
    `36 Mins`, `48 Hours`, or `12 Days`
    :param seconds: the amount of seconds to format
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


def pluralize(number: int, word: str) -> str:
    """
    If the provided number is not `1`, an `s` will be
    appended to the provided word
    :param number: the number to run pluralisation against
    :param word: the word to pluralize
    """
    if number != 1:
        return f'{word}s'
    return word


def get_session_data(uuid: PlayerUUID, session_id=1, as_dict=False):
    with sqlite3.connect(f'{REL_PATH}/database/core.db') as conn:
        cursor = conn.cursor()

        cursor.execute(
            "SELECT * FROM sessions WHERE session=? AND uuid=?", (session_id, uuid))
        session_data = cursor.fetchone()

        if as_dict:
            column_names = [desc[0] for desc in cursor.description]
            session_data = dict(zip(column_names, session_data))

    return session_data


def timezone_relative_timestamp(timestamp: int | float):
    """
    Adds local time difference to a UTC timestamp
    :param timestamp: the timestamp to modify
    """
    now_timestamp = datetime.now().timestamp()
    utcnow_timestamp = datetime.utcnow().timestamp()
    timezone_difference = now_timestamp - utcnow_timestamp

    return timestamp + timezone_difference


def comma_separated_to_list(comma_seperated_list: str) -> list:
    """
    Converts a comma seperated list (string) to a list of strings

    Example `"foo,bar"` -> `["foo", "bar"]`
    :param comma_seperated_list: the comma seperated list of items
    """
    if comma_seperated_list:
        return comma_seperated_list.split(',')
    return []


def setup_database_schema(schema_fp=f"{REL_PATH}/schema.sql", db_fp=config.DB_FILE_PATH) -> None:
    with open(schema_fp) as db_schema_file:
        db_schema_setup = db_schema_file.read()

    with sqlite3.connect(db_fp) as conn:
        cursor = conn.cursor()
        cursor.executescript(db_schema_setup)
