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
def get_hypixel_data(uuid: str):
    with open('./database/apikeys.json', 'r') as keyfile:
        allkeys = json.load(keyfile)['keys']
    key = random.choice(list(allkeys))

    return stats_session.get(f"https://api.hypixel.net/player?key={allkeys[key]}&uuid={uuid}", timeout=10).json()

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
    with open('./database/apikeys.json', 'r') as datafile:
        allkeys = json.load(datafile)['keys']
    key = random.choice(list(allkeys))

    data = requests.get(f"https://api.hypixel.net/player?key={allkeys[key]}&uuid={uuid}", timeout=10).json()
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
    with open('./database/apikeys.json', 'r') as datafile:
        allkeys = json.load(datafile)['keys']
    key = random.choice(list(allkeys))
    response = requests.get(f"https://api.hypixel.net/player?key={allkeys[key]}&uuid={uuid}", timeout=10)
    data = response.json()
    if data['player'] is None:
        return False
    stat_keys = ["Experience", "wins_bedwars", "losses_bedwars", "final_kills_bedwars", "final_deaths_bedwars", "kills_bedwars", "deaths_bedwars", "beds_broken_bedwars", "beds_lost_bedwars", "games_played_bedwars", "eight_one_wins_bedwars", "eight_one_losses_bedwars", "eight_one_final_kills_bedwars", "eight_one_final_deaths_bedwars", "eight_one_kills_bedwars", "eight_one_deaths_bedwars", "eight_one_beds_broken_bedwars", "eight_one_beds_lost_bedwars", "eight_one_games_played_bedwars", "eight_two_wins_bedwars", "eight_two_losses_bedwars", "eight_two_final_kills_bedwars", "eight_two_final_deaths_bedwars", "eight_two_kills_bedwars", "eight_two_deaths_bedwars", "eight_two_beds_broken_bedwars", "eight_two_beds_lost_bedwars", "eight_two_games_played_bedwars", "four_three_wins_bedwars", "four_three_losses_bedwars", "four_three_final_kills_bedwars", "four_three_final_deaths_bedwars", "four_three_kills_bedwars", "four_three_deaths_bedwars", "four_three_beds_broken_bedwars", "four_three_beds_lost_bedwars", "four_three_games_played_bedwars", "four_four_wins_bedwars", "four_four_losses_bedwars", "four_four_final_kills_bedwars", "four_four_final_deaths_bedwars", "four_four_kills_bedwars", "four_four_deaths_bedwars", "four_four_beds_broken_bedwars", "four_four_beds_lost_bedwars", "four_four_games_played_bedwars"]
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
            uuid = MCUUID(name=username).uuid
            name = MCUUID(name=username).name
        except KeyError:
            await interaction.response.send_message("That player does not exist!")
            return
    return name, uuid
