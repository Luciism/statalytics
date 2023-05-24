import random
import json
import typing
import sqlite3
import discord
import requests

from discord import app_commands
from mcuuid import MCUUID
from requests_cache import CachedSession

from datetime import datetime

stats_session = CachedSession(cache_name='cache/stats_cache', expire_after=300, ignored_parameters=['key'])
skin_session = CachedSession(cache_name='cache/skin_cache', expire_after=300, ignored_parameters=['key'])

# Username autofill
async def username_autocompletion(interaction: discord.Interaction, current: str) -> typing.List[app_commands.Choice[str]]: #pylint: disable=unused-argument
    data = []

    with sqlite3.connect('./database/autofill.db') as conn:
        cursor = conn.cursor()
        result = cursor.execute("SELECT * FROM autofill WHERE LOWER(username) LIKE LOWER(?)", (fr'%{current.lower()}%',))

    for row in result:
        if len(data) < 25:
            data.append(app_commands.Choice(name=row[2], value=row[2]))
        else:
            break
    return data

# Session autofill
async def session_autocompletion(interaction: discord.Interaction, current: str) -> typing.List[app_commands.Choice[str]]: #pylint: disable=unused-argument
    username_option = next((opt for opt in interaction.data['options'] if opt['name'] == 'username'), None)
    if username_option:
        username = username_option.get('value')
        uuid = MCUUID(name=username).uuid
    else:
        with sqlite3.connect('./database/linked_accounts.db') as conn:
            cursor = conn.cursor()
            cursor.execute(f"SELECT * FROM linked_accounts WHERE discord_id = {interaction.user.id}")
            linked_data = cursor.fetchone()
        if not linked_data:
            return []
        uuid = linked_data[1]
    with sqlite3.connect('./database/sessions.db') as conn:
        cursor = conn.cursor()
        cursor.execute(f"SELECT * FROM sessions WHERE uuid='{uuid}'")
        session_data = cursor.fetchall()
    data = []
    for session in session_data:
        data.append(app_commands.Choice(name=session[0], value=session[0]))
    return data

# Get cooldown
def check_subscription(interaction: discord.Interaction) -> typing.Optional[app_commands.Cooldown]:
    with sqlite3.connect('./database/subscriptions.db') as conn:
        cursor = conn.cursor()
        cursor.execute(f"SELECT * FROM subscriptions WHERE discord_id = {interaction.user.id}")
        subscription = cursor.fetchone()
    if subscription:
        return app_commands.Cooldown(1, 0.0)
    return app_commands.Cooldown(1, 3.5)

# Get hypixel data
def get_hypixel_data(uuid: str, cache: bool=True):
    with open('./database/apikeys.json', 'r') as keyfile:
        all_keys = json.load(keyfile)['hypixel']
    key = all_keys[random.choice(list(all_keys))]

    if cache: data = stats_session.get(f"https://api.hypixel.net/player?key={key}&uuid={uuid}", timeout=10).json()
    else: data = requests.get(f"https://api.hypixel.net/player?key={key}&uuid={uuid}", timeout=10).json()
    return data

# Get linked data
def get_linked_data(discord_id: int):
    with sqlite3.connect('./database/linked_accounts.db') as conn:
        cursor = conn.cursor()
        cursor.execute(f"SELECT * FROM linked_accounts WHERE discord_id = {discord_id}")
        return cursor.fetchone()

# Get subscription data
def get_subscription(discord_id: int):
    with sqlite3.connect('./database/subscriptions.db') as conn:
        cursor = conn.cursor()
        cursor.execute(f"SELECT * FROM subscriptions WHERE discord_id = {discord_id}")
        return cursor.fetchone()

# Update command stats
def update_command_stats(discord_id, command):
    with sqlite3.connect('./database/command_usage.db') as conn:
        cursor = conn.cursor()

        cursor.execute(f"SELECT * FROM overall WHERE discord_id = {discord_id}")
        if not cursor.fetchone(): cursor.execute('INSERT INTO overall (discord_id, commands_ran) VALUES (?, ?)', (discord_id, 1))
        else: cursor.execute(f'UPDATE overall SET commands_ran = commands_ran + 1 WHERE discord_id = {discord_id}')

        try:
            cursor.execute(f"SELECT * FROM {command} WHERE discord_id = {discord_id}")
            current_commands_ran = cursor.fetchone()
        except sqlite3.OperationalError:
            cursor.execute(f"CREATE TABLE {command}( discord_id INTEGER PRIMARY KEY, commands_ran INTEGER )")
            cursor.execute(f'INSERT INTO {command} (discord_id, commands_ran) VALUES (?, ?)', (0, 0))
            current_commands_ran = None
        if not current_commands_ran: cursor.execute(f'INSERT INTO {command} (discord_id, commands_ran) VALUES (?, ?)', (discord_id, 1))
        else: cursor.execute(f'UPDATE {command} SET commands_ran = commands_ran + 1 WHERE discord_id = {discord_id}')

        cursor.execute(f'UPDATE overall SET commands_ran = commands_ran + 1 WHERE discord_id = 0')
        cursor.execute(f'UPDATE {command} SET commands_ran = commands_ran + 1 WHERE discord_id = 0')

# Account linking
def link_account(discord_tag, discord_id, name, uuid):
    with open('./database/apikeys.json', 'r') as keyfile:
        all_keys = json.load(keyfile)['hypixel']
    key = all_keys[random.choice(list(all_keys))]

    data = requests.get(f"https://api.hypixel.net/player?key={key}&uuid={uuid}", timeout=10).json()
    if not data['player']: return None
    hypixel_discord_tag = data.get('player', {}).get('socialMedia', {}).get('links', {}).get('DISCORD', None)

    # Linking Logic
    if hypixel_discord_tag:
        if discord_tag == hypixel_discord_tag:
            # Update it in the linked accounts database
            with sqlite3.connect('./database/linked_accounts.db') as conn:
                cursor = conn.cursor()
                cursor.execute(f"SELECT * FROM linked_accounts WHERE discord_id = {discord_id}")
                linked_data = cursor.fetchone()

                if not linked_data: cursor.execute("INSERT INTO linked_accounts (discord_id, uuid) VALUES (?, ?)", (discord_id, uuid))
                else: cursor.execute("UPDATE linked_accounts SET uuid = ? WHERE discord_id = ?", (uuid, discord_id))


            # Update autofill
            with sqlite3.connect('./database/subscriptions.db') as conn:
                cursor = conn.cursor()
                cursor.execute(f"SELECT * FROM subscriptions WHERE discord_id = {discord_id}")
                subscription = cursor.fetchone()

            if subscription:
                with sqlite3.connect('./database/autofill.db') as conn:
                    cursor = conn.cursor()
                    cursor.execute(f"SELECT * FROM autofill WHERE discord_id = {discord_id}")
                    autofill_data = cursor.fetchone()

                    if not autofill_data:
                        query = "INSERT INTO autofill (discord_id, uuid, username) VALUES (?, ?, ?)"
                        cursor.execute(query, (discord_id, uuid, name))
                    else:
                        query = "UPDATE autofill SET uuid = ?, username = ? WHERE discord_id = ?"
                        cursor.execute(query, (uuid, name, discord_id))
            return True
        return False
    return None

# Start session
def start_session(uuid, session):
    with open('./database/apikeys.json', 'r') as keyfile:
        all_keys = json.load(keyfile)['hypixel']
    key = all_keys[random.choice(list(all_keys))]

    data = requests.get(f"https://api.hypixel.net/player?key={key}&uuid={uuid}", timeout=10).json()
    if data['player'] is None:
        return False
    with open('./config.json', 'r') as datafile:
        stat_keys = json.load(datafile)['tracked_bedwars_stats']
    stat_values = {
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
        row = cursor.fetchone()

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

# Authenticate Linked User
def update_autofill(discord_id, uuid, username):
    subscription = get_subscription(discord_id)

    if subscription:
        with sqlite3.connect('../bot/database/autofill.db') as conn:
            cursor = conn.cursor()
            cursor.execute(f"SELECT * FROM autofill WHERE discord_id = {discord_id}")
            autofill_data = cursor.fetchone()

            if not autofill_data:
                query = "INSERT INTO autofill (discord_id, uuid, username) VALUES (?, ?, ?)"
                cursor.execute(query, (discord_id, uuid, username))
            elif autofill_data[2] != username:
                query = "UPDATE autofill SET uuid = ?, username = ? WHERE discord_id = ?"
                cursor.execute(query, (uuid, username, discord_id))

async def authenticate_user(username, interaction):
    if username is None:
        with sqlite3.connect('./database/linked_accounts.db') as conn:
            cursor = conn.cursor()
            cursor.execute(f"SELECT * FROM linked_accounts WHERE discord_id = {interaction.user.id}")
            linked_data = cursor.fetchone()
        if linked_data:
            uuid = linked_data[1]
            name = MCUUID(uuid=uuid).name
            update_autofill(interaction.user.id, uuid, name)
        else:
            await interaction.response.send_message("You are not linked! Either specify a player or link your account using `/link`!")
            return
    else:
        try:
            if len(username) <= 16:
                uuid = MCUUID(name=username).uuid
                name = MCUUID(name=username).name
            else:
                name = MCUUID(uuid=username).name
                uuid = username
        except KeyError:
            await interaction.response.send_message("That player does not exist!")
            return
    return name, uuid


async def get_smart_session(interaction, session, username, uuid):
    with sqlite3.connect('./database/sessions.db') as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM sessions WHERE session=? AND uuid=?", (int(str(session)[0]), uuid))
        session_data = cursor.fetchone()
        if not session_data:
            cursor.execute(f"SELECT session FROM sessions WHERE uuid='{uuid}' ORDER BY session ASC")
            session_data = cursor.fetchone()

    if not session_data:
        await interaction.response.defer()
        response = start_session(uuid, session=1)

        if response is True: await interaction.followup.send(f"**{username}** has no active sessions so one was created!")
        else: await interaction.followup.send(f"**{username}** has never played before!")
        return False
    elif session_data[0] != session and session != 100: 
        await interaction.response.send_message(f"**{username}** doesn't have an active session with ID: `{session}`!")
        return False

    return session_data

def start_historical(uuid: str, method: str) -> None:
    hypixel_data = get_hypixel_data(uuid, cache=False)

    with open('./config.json', 'r') as datafile:
        stat_keys: list = json.load(datafile)['tracked_bedwars_stats']
    stat_values = [uuid, hypixel_data["player"].get("achievements", {}).get("bedwars_level", 0)]

    for key in stat_keys:
        stat_values.append(hypixel_data["player"].get("stats", {}).get("Bedwars", {}).get(key, 0))
    stat_keys.insert(0, 'level')
    stat_keys.insert(0, 'uuid')

    with sqlite3.connect('./database/historical.db') as conn:
        cursor = conn.cursor()

        keys = ', '.join(stat_keys)
        cursor.execute(f"INSERT INTO {method} ({keys}) VALUES ({', '.join('?'*len(stat_keys))})", stat_values)

def save_historical(local_data: tuple, hypixel_data: tuple, table: str):
    historical_values = [hypixel_data[0], hypixel_data[1]]

    for i, value in enumerate(hypixel_data[1:]):
        historical_values.append(value - local_data[i+1])

    with open('./config.json', 'r') as datafile:
        stat_keys = ['uuid', 'level', 'stars_gained']
        stat_keys.extend(json.load(datafile)['tracked_bedwars_stats'])

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
    """Attempts to fetch discord id from linked database"""
    with sqlite3.connect('./database/linked_accounts.db') as conn:
        cursor = conn.cursor()
        cursor.execute(f"SELECT discord_id FROM linked_accounts WHERE uuid = '{uuid}'")
        discord_id = cursor.fetchone()
    return None if not discord_id else discord_id[0]

def get_time_config(discord_id: int) -> tuple:
    with sqlite3.connect('./database/historical.db') as conn:
        cursor = conn.cursor()

        if discord_id:
            cursor.execute(f"SELECT * FROM configuration WHERE discord_id = '{discord_id}'")
            config_data = cursor.fetchone()
            if config_data:
                return config_data[1:]
            else: return 0, 0
        else: return 0, 0
