"""A set of useful functions used throughout the bot"""

import os
import random
import json
import time
import typing
import sqlite3
import discord
import requests
import traceback
from datetime import datetime, timedelta

from discord import app_commands
from mcuuid import MCUUID
from requests_cache import CachedSession

from helper.ui import ModesView
from helper.calctools import get_player_dict

stats_session = CachedSession(cache_name='cache/stats_cache', expire_after=300, ignored_parameters=['key'])
skin_session = CachedSession(cache_name='cache/skin_cache', expire_after=300, ignored_parameters=['key'])



def get_config() -> dict:
    """
    Returns json data from the `config.json` file
    """
    with open('./config.json', 'r') as datafile:
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
    with sqlite3.connect('./database/voting.db') as conn:
        cursor = conn.cursor()

        cursor.execute(f'SELECT * FROM voting_data WHERE discord_id = {discord_id}')
        return cursor.fetchone()


async def username_autocompletion(interaction: discord.Interaction, current: str) -> typing.List[app_commands.Choice[str]]:
    """
    Interaction username autocomplete
    Paramaters will be handled automatically by discord.py
    """
    data: list = []

    with sqlite3.connect('./database/autofill.db') as conn:
        cursor = conn.cursor()
        result = cursor.execute("SELECT * FROM autofill WHERE LOWER(username) LIKE LOWER(?)", (fr'%{current.lower()}%',))

    for row in result:
        if len(data) < 25:
            data.append(app_commands.Choice(name=row[2], value=row[2]))
        else:
            break
    return data


async def session_autocompletion(interaction: discord.Interaction, current: str) -> typing.List[app_commands.Choice[str]]:
    """
    Interaction session autocomplete
    Paramaters will be handled automatically by discord.py
    """
    username_option = next((opt for opt in interaction.data['options'] if opt['name'] == 'username'), None)
    if username_option:
        username = username_option.get('value')
        uuid: str = MCUUID(name=username).uuid
    else:
        with sqlite3.connect('./database/linked_accounts.db') as conn:
            cursor = conn.cursor()
            cursor.execute(f"SELECT * FROM linked_accounts WHERE discord_id = {interaction.user.id}")
            linked_data: tuple = cursor.fetchone()
        if not linked_data:
            return []
        uuid: str = linked_data[1]
    with sqlite3.connect('./database/sessions.db') as conn:
        cursor = conn.cursor()
        cursor.execute(f"SELECT * FROM sessions WHERE uuid='{uuid}'")
        session_data = cursor.fetchall()
    data = []
    for session in session_data:
        data.append(app_commands.Choice(name=session[0], value=session[0]))
    return data


def get_command_cooldown(interaction: discord.Interaction) -> typing.Optional[app_commands.Cooldown]:
    """
    Gets interaction cooldown based on subscription and voting status.
    Subscription = 0 seconds
    Recent vote = 1.75
    Nothing = 3.5

    Paramaters will be handled automatically by discord.py
    """
    with sqlite3.connect('./database/subscriptions.db') as conn:
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


def get_hypixel_data(uuid: str, cache: bool=True) -> dict:
    """
    Fetch a users hypixel data from hypixel's api
    :param uuid: The uuid of the user's data to fetch
    :param cache: Whether to use caching or not
    """
    with open('./database/apikeys.json', 'r') as keyfile:
        all_keys: dict = json.load(keyfile)['hypixel']
    key: str = all_keys[random.choice(list(all_keys))]

    if cache:
        data: dict = stats_session.get(f"https://api.hypixel.net/player?key={key}&uuid={uuid}", timeout=10).json()
    else:
        data: dict = requests.get(f"https://api.hypixel.net/player?key={key}&uuid={uuid}", timeout=10).json()
    return data


def get_linked_data(discord_id: int) -> tuple:
    """
    Returns a users linked data from linked database
    :param discord_id: The discord id of user's linked data to be retrieved
    """
    with sqlite3.connect('./database/linked_accounts.db') as conn:
        cursor = conn.cursor()
        cursor.execute(f"SELECT * FROM linked_accounts WHERE discord_id = {discord_id}")
        return cursor.fetchone()


def get_subscription(discord_id: int) -> tuple:
    """
    Returns a users subscription data from subscription database
    :param discord_id: The discord id of user's subscription data to be retrieved
    """
    with sqlite3.connect('./database/subscriptions.db') as conn:
        cursor = conn.cursor()
        cursor.execute(f"SELECT * FROM subscriptions WHERE discord_id = {discord_id}")
        return cursor.fetchone()


def update_command_stats(discord_id: int, command: str) -> None:
    """
    Updates command usage stats for passed command.
    If command doesn't exist in database, a new table will be created.
    :param discord_id: The user that ran he command
    """
    with sqlite3.connect('./database/command_usage.db') as conn:
        cursor = conn.cursor()

        cursor.execute(f"SELECT * FROM overall WHERE discord_id = {discord_id}")
        if not cursor.fetchone():
            cursor.execute('INSERT INTO overall (discord_id, commands_ran) VALUES (?, ?)', (discord_id, 1))
        else:
            cursor.execute(f'UPDATE overall SET commands_ran = commands_ran + 1 WHERE discord_id = {discord_id}')

        try:
            cursor.execute(f"SELECT * FROM {command} WHERE discord_id = {discord_id}")
            current_commands_ran: tuple = cursor.fetchone()
        except sqlite3.OperationalError:
            cursor.execute(f"CREATE TABLE {command}( discord_id INTEGER PRIMARY KEY, commands_ran INTEGER )")
            cursor.execute(f'INSERT INTO {command} (discord_id, commands_ran) VALUES (?, ?)', (0, 0))
            current_commands_ran = None

        if not current_commands_ran:
            cursor.execute(f'INSERT INTO {command} (discord_id, commands_ran) VALUES (?, ?)', (discord_id, 1))
        else:
            cursor.execute(f'UPDATE {command} SET commands_ran = commands_ran + 1 WHERE discord_id = {discord_id}')

        cursor.execute(f'UPDATE overall SET commands_ran = commands_ran + 1 WHERE discord_id = 0')
        cursor.execute(f'UPDATE {command} SET commands_ran = commands_ran + 1 WHERE discord_id = 0')


def insert_linked_data(discord_id: int, uuid: str) -> None:
    """
    Inserts linked account data into database
    :param discord_id: the discord id of the relative user
    :param uuid: the minecraft uuid of the relvative user
    """
    with sqlite3.connect('./database/linked_accounts.db') as conn:
        cursor = conn.cursor()
        cursor.execute(f"SELECT * FROM linked_accounts WHERE discord_id = {discord_id}")
        linked_data = cursor.fetchone()

        if not linked_data:
            cursor.execute("INSERT INTO linked_accounts (discord_id, uuid) VALUES (?, ?)", (discord_id, uuid))
        else:
            cursor.execute("UPDATE linked_accounts SET uuid = ? WHERE discord_id = ?", (uuid, discord_id))


def link_account(discord_tag: str, discord_id: int, name: str, uuid: str) -> bool | None:
    """
    Attempt to link an discord account to a hypixel account
    :param discord_tag: The discord user's full tag eg: Example#1234
    :param discord_id: The discord user's id
    :param name: The username of the hypixel account being linked
    :param uuid: The uuid of the hypixel account being linked
    """
    hypixel_data = get_hypixel_data(uuid=uuid, cache=False)
    if not hypixel_data['player']:
        return None
    hypixel_discord_tag: str = hypixel_data.get('player', {}
        ).get('socialMedia', {}
        ).get('links', {}
        ).get('DISCORD', None)

    # Linking Logic
    if hypixel_discord_tag:
        if discord_tag == hypixel_discord_tag:
            insert_linked_data(discord_id=discord_id, uuid=uuid)
            update_autofill(discord_id=discord_id, uuid=uuid, username=name)
            return True
        return False
    return None


def start_session(uuid: str, session: int) -> bool:
    """
    Initiate a bedwars stats session
    :param uuid: The uuid of the player to initiate a session for
    :param session: The id of the session being initiated
    """
    with open('./database/apikeys.json', 'r') as keyfile:
        all_keys: dict = json.load(keyfile)['hypixel']
    key: str = all_keys[random.choice(list(all_keys))]

    data: dict = requests.get(f"https://api.hypixel.net/player?key={key}&uuid={uuid}", timeout=10).json()
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

    with sqlite3.connect('./database/sessions.db') as conn:
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM sessions WHERE session=? AND uuid=?", (session, uuid))
        row: tuple = cursor.fetchone()

        if not row:
            columns = ', '.join(stat_values.keys())
            values = ', '.join(['?' for _ in stat_values.values()])
            query = f"INSERT INTO sessions ({columns}) VALUES ({values})"
            cursor.execute(query, tuple(stat_values.values()))
        else:
            set_clause = ', '.join([f"{column} = ?" for column in stat_values.keys()])
            query = f"UPDATE sessions SET {set_clause} WHERE session=? AND uuid=?"
            values = list(stat_values.values()) + [session, uuid]
            cursor.execute(query, tuple(values))
        conn.commit()
    return True


def update_autofill(discord_id: int, uuid: str, username: str) -> None:
    """
    Updates autofill for a user, this will be helpful if a user has changed their ign
    :param discord_id: The discord id of the target linked user
    :param uuid: The uuid of the target linked user
    :param username: The updated username of the target linked user
    """
    subscription: tuple = get_subscription(discord_id)
    if subscription:
        with sqlite3.connect('../bot/database/autofill.db') as conn:
            cursor = conn.cursor()
            cursor.execute(f"SELECT * FROM autofill WHERE discord_id = {discord_id}")
            autofill_data: tuple = cursor.fetchone()

            if not autofill_data:
                query = "INSERT INTO autofill (discord_id, uuid, username) VALUES (?, ?, ?)"
                cursor.execute(query, (discord_id, uuid, username))
            elif autofill_data[2] != username:
                query = "UPDATE autofill SET uuid = ?, username = ? WHERE discord_id = ?"
                cursor.execute(query, (uuid, username, discord_id))


async def authenticate_user(username: str, interaction: discord.Interaction) -> tuple[str, str] | None:
    """
    Get formatted username & uuid of a user from their minecraft ign / uuid
    :param username: The minecraft ign of the player to return (can also take a uuid)
    :param interaction: The discord interaction object used
    """
    if username is None:
        linked_data = get_linked_data(interaction.user.id)
        if linked_data:
            uuid: str = linked_data[1]
            name: str = MCUUID(uuid=uuid).name
            update_autofill(interaction.user.id, uuid, name)
        else:
            await interaction.followup.send("You are not linked! Either specify a player or link your account using `/link`!")
            return
    else:
        try:
            if len(username) <= 16:
                uuid: str = MCUUID(name=username).uuid
                name: str = MCUUID(name=username).name
            else:
                name: str = MCUUID(uuid=username).name
                uuid: str = username
                if not name:
                    raise KeyError
        except KeyError:
            await interaction.followup.send("That player does not exist!")
            return
    return name, uuid


async def get_smart_session(interaction: discord.Interaction, session: int, username: str, uuid: str) -> tuple | bool:
    """
    Dynamically gets a session of a user
    If session is 100, the first session to exist will be returned
    :param interaction: The discord interaction object used
    :param session: The session to attempt to be retrieved
    :param username: The username of the session owner
    :param uuid: The uuid of the session owner
    """
    with sqlite3.connect('./database/sessions.db') as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM sessions WHERE session=? AND uuid=?", (int(str(session)[0]), uuid))
        session_data: tuple = cursor.fetchone()

        if not session_data:
            cursor.execute(f"SELECT session FROM sessions WHERE uuid='{uuid}' ORDER BY session ASC")
            session_data: tuple = cursor.fetchone()

    if not session_data:
        response: bool = start_session(uuid, session=1)

        if response is True:
            await interaction.followup.send(f"**{username}** has no active sessions so one was created!")
        else:
            await interaction.followup.send(f"**{username}** has never played before!")
        return False

    elif session_data[0] != session and session != 100: 
        await interaction.followup.send(f"**{username}** doesn't have an active session with ID: `{session}`!")
        return False

    return session_data


def start_historical(uuid: str) -> None:
    """
    Initiates historical stat tracking (daily, weekly, etc)
    :param uuid: The uuid of the player's historical stats being initiated
    """
    hypixel_data: dict = get_hypixel_data(uuid, cache=False)
    hypixel_data = get_player_dict(hypixel_data)

    stat_keys: dict = get_config()['tracked_bedwars_stats']
    stat_values = [uuid, hypixel_data.get("achievements", {}).get("bedwars_level", 0)]

    for key in stat_keys:
        stat_values.append(hypixel_data.get("stats", {}).get("Bedwars", {}).get(key, 0))

    stat_keys.insert(0, 'level')
    stat_keys.insert(0, 'uuid')
    keys = ', '.join(stat_keys)

    trackers = ('daily', 'weekly', 'monthly', 'yearly')
    for tracker in trackers:
        with sqlite3.connect('./database/historical.db') as conn:
            cursor = conn.cursor()
            cursor.execute(f"SELECT uuid FROM {tracker} WHERE uuid = '{uuid}'")
            if not cursor.fetchone():
                cursor.execute(f"INSERT INTO {tracker} ({keys}) VALUES ({', '.join('?'*len(stat_keys))})", stat_values)


def save_historical(local_data: tuple, hypixel_data: tuple, table: str) -> None:
    """
    Saves historical data to a specified table, typically used when historical stats reset.
    Creates new table if specified table doesn't exist
    :param local_data: The historical starting data
    :param hypixel_data: The current hypixel data
    :param table: The name of the table to save the historical data to
    """
    historical_values = [hypixel_data[0], hypixel_data[1]]

    for i, value in enumerate(hypixel_data[1:]):
        historical_values.append(value - local_data[i+1])

    stat_keys = ['uuid', 'level', 'stars_gained']
    stat_keys.extend(get_config()['tracked_bedwars_stats'])

    with sqlite3.connect('./database/historical.db') as conn:
        cursor = conn.cursor()

        cursor.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name='{table}'")
        if not cursor.fetchone():
            columns = ', '.join([f'{key} INTEGER' for key in stat_keys[1:]])
            cursor.execute(f"CREATE TABLE {table} (uuid TEXT PRIMARY KEY, {columns})")

        cursor.execute(f"SELECT uuid FROM {table} WHERE uuid = '{hypixel_data[0]}'")
    
        if not cursor.fetchone():
            keys = ', '.join(stat_keys)
            cursor.execute(f"INSERT INTO {table} ({keys}) VALUES ({', '.join('?'*len(stat_keys))})", historical_values)


def uuid_to_discord_id(uuid: str) -> int | None:
    """
    Attempts to fetch discord id from linked database
    :param uuid: The uuid of the player to find linked data for
    """
    with sqlite3.connect('./database/linked_accounts.db') as conn:
        cursor = conn.cursor()
        cursor.execute(f"SELECT discord_id FROM linked_accounts WHERE uuid = '{uuid}'")
        discord_id = cursor.fetchone()
    return None if not discord_id else discord_id[0]


def get_time_config(discord_id: int) -> tuple:
    """
    Attempt to get time configuration data for specified discord id
    :param discord_id: The discord id of the relative user
    """
    with sqlite3.connect('./database/historical.db') as conn:
        cursor = conn.cursor()

        if discord_id:
            cursor.execute(f"SELECT * FROM configuration WHERE discord_id = '{discord_id}'")
            config_data = cursor.fetchone()
            if config_data:
                return config_data[1:]
            else:
                return 0, 0
        else:
            return 0, 0


async def get_lookback_eligiblility(interaction: discord.Interaction, discord_id: int) -> bool:
    """
    Returns the amount of days back a user can check a player's historical stats
    :param interaction: The discord interaction object used
    :param discord_id: The relative discord_id to be checked
    """
    subscription = None
    if discord_id:
        subscription = get_subscription(discord_id=discord_id)

    if not subscription or not discord_id:
        subscription = get_subscription(discord_id=interaction.user.id)

    if subscription:
        if 'basic' in subscription[1]:
            return 60
        elif 'pro' in subscription[1]:
            return -1
        return 30
    return 30


async def message_invalid_lookback(interaction: discord.Interaction, max_lookback) -> None:
    """
    Responds to a interaction with an max lookback exceeded message
    :param interaction: The discord interaction object used
    :param max_lookback: The maximum lookback the user had availiable
    """
    embed_color = get_embed_color('primary')
    embed = discord.Embed(
        title='Maximum lookback exceeded!',
        description=f"The maximum lookback for viewing that player's historical stats is {max_lookback}!",
        color=embed_color
    )

    embed.add_field(name="How it works:", value=f"""
        \- You can view history up to `{max_lookback}` days with your's or the checked player's plan.
        \- You can view longer history if you or the checked player has a premium plan.
    """.replace('   ', ''), inline=False)

    embed.add_field(name='Limits', value="""
        \- Free tier maximum lookback - 30 days
        \- Basic tier maxmum lookback  - 60 days
        \- Pro tier maximum lookback - unlimited
    """.replace('   ', ''), inline=False)

    await interaction.followup.send(embed=embed)


def skin_from_file() -> bytes:
    """Loads a steve skin from file"""
    with open('./assets/steve.png', 'rb') as f:
        return f.read()


def fetch_skin_model(uuid: int, size: int) -> bytes:
    """
    Fetches a 3d skin model visage.surgeplay.com
    If something goes wrong, a steve skin will returned
    :param uuid: The uuid of the relative player
    :param size: The skin render size in pixels
    """
    try:
        skin_res = skin_session.get(f'https://visage.surgeplay.com/bust/{size}/{uuid}', timeout=3).content
    except (requests.exceptions.ReadTimeout, requests.exceptions.ConnectTimeout):
        skin_res = skin_from_file()
    return skin_res


def ordinal(n: int) -> str:
    """
    Formats a day for example '21' would be '21st'
    :param n: The number to format
    """
    return "th" if 4 <= n % 100 <= 20 else {1: "st", 2: "nd", 3: "rd"}.get(n % 10, "th")


def get_owned_themes(discord_id: int) -> list:
    """
    Returns a list of themes owned by user relative to the passed discord id
    :param discord_id: The relative discord user
    """
    with sqlite3.connect('./database/voting.db') as conn:
        cursor = conn.cursor()
        cursor.execute(f"SELECT owned_themes FROM owned_themes WHERE discord_id = {discord_id}")
        owned_themes = cursor.fetchone()

    if owned_themes and owned_themes[0]:
        themes_list = owned_themes[0].split(',')
        return themes_list
    return []


async def yearly_eligibility(interaction: discord.Interaction, discord_id: int | None) -> bool:
    """
    Checks if a user is able to use yearly stats commands and responds accordingly
    :param interaction: the discord interaction object
    :param discord_id: the discord id of the linked player being checked
    """
    subscription = None
    if discord_id:
        subscription = get_subscription(discord_id=discord_id)

    if not subscription and not get_subscription(interaction.user.id):
        embed_color = get_embed_color('primary')
        embed = discord.Embed(
            title="That player doesn't have premium!",
            description='In order to view yearly stats, a [premium subscription](https://statalytics.net/store) is required!',
            color=embed_color
        )

        embed.add_field(name='How does it work?', value="""
            \- You can view any player's yearly stats if you have a premium subscription.
            \- You can view a player's yearly stats if they have a premium subscription.\n
            Yearly stats can be tracked but not viewed without a premium subscription
        """.replace('   ', ''))
        await interaction.followup.send(embed=embed)
        return False
    return True


def discord_message(discord_id):
    """
    Chooses a random message to send if the discord id has no subscription
    :param discord_id: the discord id of the relative user
    """
    if get_subscription(discord_id):
        return None

    if random.choice(([False]*5) + ([True]*2)):
        with open('./database/discord_messages.json', 'r') as datafile:
            data = json.load(datafile)
        return random.choice(data['active_messages'])
    return None


async def send_generic_renders(interaction: discord.Interaction,
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

    func(mode="Overall", **kwargs)
    view = ModesView(user=interaction.user.id, inter=interaction, mode='Select a mode')
    await interaction.edit_original_response(
        content=message,
        attachments=[
            discord.File(f"./database/activerenders/{interaction.id}/overall.png")],
        view=view
    )
    
    func(mode="Solos", **kwargs)
    func(mode="Doubles", **kwargs)
    func(mode="Threes", **kwargs)
    func(mode="Fours", **kwargs)
    func(mode="4v4", **kwargs)


def get_command_users():
    """
    Returns total amount of users to have run a command
    """
    with sqlite3.connect('./database/command_usage.db') as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT COUNT(*) FROM overall')
        total_users = cursor.fetchone()[0] - 1
    return total_users


def reset_historical(method: str, table_format: str, condition: str):
    """
    Loops through historical and resets each row if a condition is met
    :param method: The historical type (daily, weekly, etc)
    :param table_format: The datetime strftime format for the table name
    :param condition: The condition to be evaluated to determine whether or not to reset
    """
    # Get all linked accounts
    with sqlite3.connect('./database/linked_accounts.db') as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM linked_accounts')
        row = cursor.fetchone()

        linked_data = {}
        while row:
            linked_data[row[1]] = row[0]
            row = cursor.fetchone()

    # Get all configuration and historical
    with sqlite3.connect('./database/historical.db') as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM configuration')
        row = cursor.fetchone()

        config_data = {}
        while row:
            config_data[row[0]] = row
            row = cursor.fetchone()

        cursor.execute(f'SELECT * FROM {method}')
        historical_data = cursor.fetchall()

    # Reset all historical that is at the correct time
    utc_now = datetime.utcnow()
    for historical in historical_data:
        start_time = time.time()
        linked_account = linked_data.get(historical[0])
        if linked_account:
            time_preference = config_data.get(linked_account, (0, 0, 0))
            gmt_offset, hour = time_preference[1], time_preference[2]
        else:
            gmt_offset, hour = 0, 0

        timezone = utc_now + timedelta(hours=gmt_offset)

        if eval(condition) and timezone.hour == hour:
            hypixel_data = get_hypixel_data(historical[0], cache=False)
            hypixel_data = get_player_dict(hypixel_data)

            stat_keys: list = get_config()['tracked_bedwars_stats']
            stat_values = [hypixel_data.get("achievements", {}).get("bedwars_level", 0)]

            for key in stat_keys:
                stat_values.append(hypixel_data.get("stats", {}).get("Bedwars", {}).get(key, 0))
            stat_keys.insert(0, 'level')

            with sqlite3.connect('./database/historical.db') as conn:
                cursor = conn.cursor()

                set_clause = ', '.join([f"{column} = ?" for column in stat_keys])
                cursor.execute(f"UPDATE {method} SET {set_clause} WHERE uuid = '{historical[0]}'", stat_values)

            stat_values.insert(0, historical[0])
            table_name = (timezone - timedelta(days=1)).strftime(table_format)
            save_historical(historical, stat_values, table=table_name)

            time_elapsed = time.time() - start_time
            if time_elapsed < 2:
                sleep_time = 2 - (time_elapsed)
                time.sleep(sleep_time)


async def log_error_msg(client: discord.Client, error: Exception):
    """
    Prints and sends an error message to discord error logs channel
    :param client: The discord.py client object
    :param error: The exception object for the error
    """
    traceback_str = ''.join(traceback.format_exception(type(error), error, error.__traceback__))
    print(traceback_str)

    if os.environ.get('STATALYTICS_ENVIRONMENT') == 'development':
        return

    config = get_config()
    await client.wait_until_ready()
    channel = client.get_channel(config.get('error_logs_channel_id'))

    if len(traceback_str) > 1988:
        for i in range(0, len(traceback_str), 1988):
            substring = traceback_str[i:i+1988]
            await channel.send(f'```cmd\n{substring}\n```')
    else:
        await channel.send(f'```cmd\n{traceback_str[-1988:]}\n```')
