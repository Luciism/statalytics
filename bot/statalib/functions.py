"""A set of useful functions used throughout the bot"""

import os
import json
import random
import typing
import sqlite3
import asyncio
import functools
from datetime import datetime, timedelta

import discord


REL_PATH = os.path.abspath(f'{__file__}/../..')


def to_thread(func: typing.Callable) -> typing.Coroutine:
    @functools.wraps(func)
    async def wrapper(*args, **kwargs):
        return await asyncio.to_thread(func, *args, **kwargs)
    return wrapper


def get_config(path: str=None):
    """
    Returns contents of the `config.json` file
    :param path: the json path to the value for example `key_1.key_2`
    """
    with open(f'{REL_PATH}/config.json', 'r') as datafile:
        config_data = json.load(datafile)

    if path:
        for key in path.split('.'):
            config_data = config_data[key]

    return config_data


STATIC_CONFIG = get_config()


def get_embed_color(embed_type: str) -> int:
    """
    Returns a base 16 integer from a hex code.
    :param embed_type: the embed color type (primary, warning, danger)
    """
    config = get_config()
    return int(config[f'embed_{embed_type}_color'], base=16)


def loading_message() -> str:
    """
    Returns loading message from the `config.json` file
    """
    return STATIC_CONFIG.get('loading_message')


def get_voting_data(discord_id: int) -> tuple:
    """
    Returns a users voting data
    :param discord_id: The discord id of the user's voting data to be fetched
    """
    with sqlite3.connect(f'{REL_PATH}/database/core.db') as conn:
        cursor = conn.cursor()

        cursor.execute(f'SELECT * FROM voting_data WHERE discord_id = {discord_id}')
        return cursor.fetchone()


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
        cursor.execute(f"SELECT overall, {command} FROM command_usage WHERE discord_id = {discord_id}")
        result = cursor.fetchone()

        if result and result[0]:
            cursor.execute(f"""
                UPDATE command_usage
                SET overall = overall + 1,
                {command} = {f'{command} + 1' if result[1] else 1}
                WHERE discord_id = {discord_id}
            """) # if command current is null, it will be set to 1
        else:
            cursor.execute(
                f"INSERT INTO command_usage (discord_id, overall, {command}) VALUES (?, ?, ?)",
                (discord_id, 1, 1)
            )


def update_command_stats(discord_id: int, command: str) -> None:
    """
    Updates command usage stats for respective command.
    :param discord_id: the user that ran he command
    :param command: the command run by the user to increment
    """
    _update_usage(command, discord_id)
    _update_usage(command, 0) # Global commands


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

        cursor.execute('SELECT COUNT(discord_id) FROM command_usage')
        result = cursor.fetchone()

    if result:
        return result[0] - 1
    return 0


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


def load_embeds(filename: str, format_values: dict=None, color: int | str=None):
    """
    Loads a dictionary of embeds into discord.Embed objects\n
    Embeds can either be in string form or in dictionary formstring embeds must\n
    use double curly braces `'{{"a": 1, "b": 2}}'` in order to escape formatting\n
    Only string embeds can have values formatted into them
    :param filename: the name of the file containing the embed json data (.json ext optional)
    :param format_values: format values into the dict (string dicts only)
    :param color: override embed color, can be integer directly or 'primary', 'warning', etc
    """
    if not filename.endswith('.json'):
        filename += '.json'

    with open(f'{REL_PATH}/assets/embeds/{filename}', 'r') as datafile:
        embed_dict: str = json.load(datafile)

    embeds = []
    if embed_dict.get('type') == 'string':
        for embed_str in embed_dict['embeds']:
            embed_str: str = embed_str.format(
                **format_values).replace("{{", "{").replace("}}", "}")

            embed = discord.Embed.from_dict(json.loads(embed_str))
            embeds.append(_set_embed_color(embed, color))
    else:
        for embed_json in embed_dict['embeds']:
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


def int_prefix(integer: int) -> str:
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


def prefix_int(integer: int):
    """
    Prefixes given number with `+` or `-` and returns it as a string
    :param integer: the integer to be prefixed
    """
    return f'{int_prefix(integer)}{integer}'


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
