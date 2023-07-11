"""A set of useful functions used throughout the bot"""

import os
import random
import json
import time
import typing
import sqlite3
import asyncio
import functools
from datetime import datetime

import discord
import requests
from requests.exceptions import ConnectTimeout, ReadTimeout
from discord import app_commands
from requests_cache import CachedSession

from .ui import ModesView
from .errors import HypixelInvalidResponseError


REL_PATH = os.path.abspath(f'{__file__}/../..')

historic_cache = CachedSession(cache_name='cache/historic_cache', expire_after=300, ignored_parameters=['key'])
stats_session = CachedSession(cache_name='cache/stats_cache', expire_after=300, ignored_parameters=['key'])
skin_session = CachedSession(cache_name='cache/skin_cache', expire_after=900, ignored_parameters=['key'])


def to_thread(func: typing.Callable) -> typing.Coroutine:
    @functools.wraps(func)
    async def wrapper(*args, **kwargs):
        return await asyncio.to_thread(func, *args, **kwargs)
    return wrapper


def get_config() -> dict:
    """
    Returns json data from the `config.json` file
    """
    with open(f'{REL_PATH}/config.json', 'r') as datafile:
        config_data = json.load(datafile)
    return config_data


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
    return get_config()['loading_message']


def get_voting_data(discord_id: int) -> tuple:
    """
    Returns a users voting data
    :param discord_id: The discord id of the user's voting data to be fetched
    """
    with sqlite3.connect(f'{REL_PATH}/database/core.db') as conn:
        cursor = conn.cursor()

        cursor.execute(f'SELECT * FROM voting_data WHERE discord_id = {discord_id}')
        return cursor.fetchone()


def get_command_cooldown(interaction: discord.Interaction
                         ) -> typing.Optional[app_commands.Cooldown]:
    """
    Gets interaction cooldown based on subscription and voting status.
    Subscription = 0 seconds
    Recent vote = 1.75
    Nothing = 3.5

    Paramaters will be handled automatically by discord.py
    """
    with sqlite3.connect(f'{REL_PATH}/database/core.db') as conn:
        cursor = conn.cursor()
        cursor.execute(f"SELECT * FROM subscriptions WHERE discord_id = {interaction.user.id}")
        subscription = cursor.fetchone()
    if subscription:
        return app_commands.Cooldown(1, 0.0)

    # If user has voted in past 24 hours
    voting_data = get_voting_data(interaction.user.id)
    current_time = time.time()
    if voting_data and ((current_time - voting_data[3]) / 3600 < 24):
        return app_commands.Cooldown(1, 1.75)

    return app_commands.Cooldown(1, 3.5)


@to_thread
def get_hypixel_data(uuid: str, cache: bool=True,
                     cache_obj: CachedSession=stats_session) -> dict:
    """
    Fetch a users hypixel data from hypixel's api
    :param uuid: The uuid of the user's data to fetch
    :param cache: Whether to use caching or not
    :param cache_obj: Use a custom cache instead of the default stats cache
    """
    with open(f'{REL_PATH}/database/apikeys.json', 'r') as keyfile:
        all_keys: dict = json.load(keyfile)['hypixel']
    key: str = all_keys[random.choice(list(all_keys.keys()))]

    options = {
        'url': f"https://api.hypixel.net/player?uuid={uuid}",
        'headers': {"API-Key": key},
        'timeout': 10
    }
    try:
        if not cache:
            return requests.get(**options).json()
        return cache_obj.get(**options).json()

    except (ReadTimeout, ConnectTimeout, json.JSONDecodeError) as exc:
        raise HypixelInvalidResponseError from exc


def get_subscription(discord_id: int) -> tuple:
    """
    Returns a users subscription data from subscription database
    :param discord_id: The discord id of user's subscription data to be retrieved
    """
    with sqlite3.connect(f'{REL_PATH}/database/core.db') as conn:
        cursor = conn.cursor()
        cursor.execute(f"SELECT * FROM subscriptions WHERE discord_id = {discord_id}")
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


async def start_session(uuid: str, session: int) -> bool:
    """
    Initiate a bedwars stats session
    :param uuid: The uuid of the player to initiate a session for
    :param session: The id of the session being initiated
    """
    with open(f'{REL_PATH}/database/apikeys.json', 'r') as keyfile:
        all_keys: dict = json.load(keyfile)['hypixel']
    key: str = all_keys[random.choice(list(all_keys))]

    data = await get_hypixel_data(uuid, cache=False)
    if data['player'] is None:
        return False

    stat_keys = get_config()['tracked_bedwars_stats']

    stat_values: dict = {
        "session": session,
        "uuid": uuid,
        "date": datetime.now().strftime("%Y-%m-%d"),
        "level": data["player"].get("achievements", {}).get("bedwars_level", 0),
    }

    for key in stat_keys:
        stat_values[key] = data["player"].get("stats", {}).get("Bedwars", {}).get(key, 0)

    with sqlite3.connect(f'{REL_PATH}/database/core.db') as conn:
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM sessions WHERE session=? AND uuid=?", (session, uuid))
        row: tuple = cursor.fetchone()

        if not row:
            columns = ', '.join(stat_values.keys())
            values = ', '.join(['?' for _ in stat_values.values()])
            query = f"INSERT INTO sessions ({columns}) VALUES ({values})"
            cursor.execute(query, tuple(stat_values.values()))
        else:
            set_clause = ', '.join([f"{column} = ?" for column in stat_values])
            query = f"UPDATE sessions SET {set_clause} WHERE session=? AND uuid=?"
            values = list(stat_values.values()) + [session, uuid]
            cursor.execute(query, tuple(values))
        conn.commit()
    return True


async def get_smart_session(interaction: discord.Interaction, session: int,
                            username: str, uuid: str) -> tuple | bool:
    """
    Dynamically gets a session of a user\n
    If session is 100, the first session to exist will be returned
    :param interaction: The discord interaction object used
    :param session: The session to attempt to be retrieved
    :param username: The username of the session owner
    :param uuid: The uuid of the session owner
    """
    with sqlite3.connect(f'{REL_PATH}/database/core.db') as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM sessions WHERE session=? AND uuid=?", (int(str(session)[0]), uuid))
        session_data: tuple = cursor.fetchone()

        if not session_data:
            cursor.execute(f"SELECT session FROM sessions WHERE uuid='{uuid}' ORDER BY session ASC")
            session_data: tuple = cursor.fetchone()

    if not session_data:
        response: bool = await start_session(uuid, session=1)

        if response is True:
            await interaction.followup.send(f"**{username}** has no active sessions so one was created!")
        else:
            await interaction.followup.send(f"**{username}** has never played before!")
        return False

    if session not in (session_data[0], 100):
        await interaction.followup.send(f"**{username}** doesn't have an active session with ID: `{session}`!")
        return False

    return session_data


def skin_from_file(skin_type: str='bust') -> bytes:
    """Loads a steve skin from file"""
    with open(f'{REL_PATH}/assets/steve_{skin_type}.png', 'rb') as skin:
        return skin.read()


@to_thread
def fetch_skin_model(uuid: int, size: int) -> bytes:
    """
    Fetches a 3d skin model visage.surgeplay.com
    If something goes wrong, a steve skin will returned
    :param uuid: The uuid of the relative player
    :param size: The skin render size in pixels
    """
    try:
        skin_res = skin_session.get(f'https://visage.surgeplay.com/bust/{size}/{uuid}', timeout=3).content
    except (ReadTimeout, ConnectTimeout):
        skin_res = skin_from_file()
    return skin_res


def ordinal(n: int) -> str:
    """
    Formats a day for example '21' would be '21st'
    :param n: The number to format
    """
    return "th" if 4 <= n % 100 <= 20 else {1: "st", 2: "nd", 3: "rd"}.get(n % 10, "th")


def discord_message(discord_id):
    """
    Chooses a random message to send if the discord id has no subscription
    :param discord_id: the discord id of the respective user
    """
    if get_subscription(discord_id):
        return None

    if random.choice(([False]*5) + ([True]*2)): # 2 in 7 chance
        with open(f'{REL_PATH}/database/discord_messages.json', 'r') as datafile:
            data = json.load(datafile)
        return random.choice(data['active_messages'])
    return None


async def handle_modes_renders(interaction: discord.Interaction,
                               func: object, kwargs: dict, message=None):
    """
    Renders and sends all modes to discord for the selected render
    :param interaction: the relative discord interaction object
    :param func: the function object to render with
    :param kwargs: the keyword arguments needed to render the image
    :param message: the message to send to discord with the image
    """
    if not message:
        message = discord_message(interaction.user.id)

    os.makedirs(f'./database/rendered/{interaction.id}')
    func(mode="Overall", **kwargs)
    view = ModesView(user=interaction.user.id, inter=interaction, mode='Select a mode')
    try:
        await interaction.edit_original_response(
            content=message,
            attachments=[
                discord.File(f"{REL_PATH}/database/rendered/{interaction.id}/overall.png")],
            view=view
        )
    except discord.errors.NotFound:
        return

    func(mode="Solos", **kwargs)
    func(mode="Doubles", **kwargs)
    func(mode="Threes", **kwargs)
    func(mode="Fours", **kwargs)
    func(mode="4v4", **kwargs)


def get_command_users():
    """
    Returns total amount of users to have run a command
    """
    with sqlite3.connect(f'{REL_PATH}/database/core.db') as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT COUNT(discord_id) FROM command_usage')
        total_users = cursor.fetchone()[0] - 1
    return total_users


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


def fname(username: str):
    """
    Returns an escaped version of a username to avoid discord markdown
    """
    return username.replace("_", "\_")
