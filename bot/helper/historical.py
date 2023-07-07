import time
import sqlite3
import random
from datetime import datetime, timedelta

import asyncio
from discord import Client, Interaction

from .errors import NoLinkedAccountError
from .handlers import log_error_msg
from .calctools import get_player_dict
from .linking import get_linked_data, uuid_to_discord_id
from .functions import (
    REL_PATH,
    get_subscription,
    get_hypixel_data,
    get_config,
    load_embeds,
    historic_cache
)


# Used to get player bound reset times that are assigned automatically.
def get_reset_time_default(uuid: str) -> tuple | None:
    """
    Gets the default reset time assigned randomly for a player
    :param uuid: The uuid of the relative player
    """
    with sqlite3.connect(f'{REL_PATH}/database/historical.db') as conn:
        cursor = conn.cursor()

        cursor.execute(f"SELECT * FROM default_reset_times WHERE uuid = '{uuid}'")
        default_data = cursor.fetchone()

    if default_data:
        return default_data[1:3]


# Used to get discord user bound reset times that are configured by the user.
def get_reset_time_configured(discord_id: int):
    """
    Gets the configured reset time set by the linked discord user
    :param discord_id: The discord id of the respective user
    """
    with sqlite3.connect(f'{REL_PATH}/database/historical.db') as conn:
        cursor = conn.cursor()

        cursor.execute(f"SELECT * FROM configuration WHERE discord_id = {discord_id}")
        configuration_data = cursor.fetchone()

    if configuration_data:
        return configuration_data[1:3]


# Uses both default & configured approaches to getting reset time.
# Configured reset time takes priority and if it doesn't exist
# default reset times will be used. If neither are present
# a reset time of midnight at GMT+0 will be used (0, 0).
def get_reset_time(uuid: str) -> tuple | None:
    """
    Attempts to get the configured reset time of the discord user\n
    If the discord user has not configured a reset time, the player's default reset time will be used
    :param uuid: The backup uuid if the discord user has no configured reset time
    """
    reset_time = False

    discord_id = uuid_to_discord_id(uuid)
    if discord_id:
        reset_time = get_reset_time_configured(discord_id)

    if not reset_time:
        reset_time = get_reset_time_default(uuid)
    return reset_time or (0, 0)



# Directly inserts or updates the default reset time of a player.
def set_reset_time_default(uuid: str, timezone: int, reset_hour: int):
    """
    Sets default reset time in historical database (player bound)
    :param uuid: The uuid of the relative player
    :param timezone: The GMT offset to insert
    :param reset_hour: The reset hour to insert
    """
    with sqlite3.connect(f'{REL_PATH}/database/historical.db') as conn:
        cursor = conn.cursor()

        cursor.execute(f"SELECT * FROM default_reset_times WHERE uuid = '{uuid}'")
        if not cursor.fetchone():
            cursor.execute(
                'INSERT INTO default_reset_times (uuid, timezone, reset_hour) VALUES (?, ?, ?)',
                (uuid, timezone, reset_hour)
            )
        else:
            cursor.execute(
                "UPDATE default_reset_times SET timezone = ?, reset_hour = ? WHERE uuid = ?",
                (timezone, reset_hour, uuid)
            )


# Updates default reset time if it is not present in the database.
# If a player is linked to discord and has configured reset time
# the default reset time will be set to the configured reset time
# otherwise a random hour will be chosen with a gmt offset of 0
def update_reset_time_default(uuid: str):
    """
    Updates a player's default reset time
    :param uuid: The uuid of the relative player
    """
    current_default = get_reset_time_default(uuid)

    if not current_default:
        discord_id = uuid_to_discord_id(uuid)

        if discord_id:
            current_configured = get_reset_time_configured(discord_id)

            if current_configured:
                set_reset_time_default(uuid, *current_configured)
                return

        set_reset_time_default(uuid, 0, random.randint(0, 23))


# Inserts or updates a discord user's configured reset time
# If the user is linked to a player, it will attempt to update
# the default reset time of that player to match the configured
# discord account bound time. This will only succeed if the
# player does not already have a default reset time set
def update_reset_time_configured(discord_id: int, value: int, method: str):
    """
    Updates discord id based reset time configuration
    :param discord_id: the discord id of the respective user
    :param value: the value associated with the method
    :param method: row name (timezone, reset_hour)
    """
    with sqlite3.connect(f'{REL_PATH}/database/historical.db') as conn:
        cursor = conn.cursor()
        cursor.execute(
            f'SELECT timezone FROM configuration WHERE discord_id = {discord_id}')

        if cursor.fetchone():
            cursor.execute(
                f'UPDATE configuration SET {method} = ? WHERE discord_id = ?', (value, discord_id))
        else:
            values = (discord_id, value, 0) if method == 'timezone' else (discord_id, 0, value)
            cursor.execute(
                'INSERT INTO configuration (discord_id, timezone, reset_hour) VALUES (?, ?, ?)', values)

        cursor.execute(
            f'SELECT timezone, reset_hour FROM configuration WHERE discord_id = {discord_id}')
        current_data = cursor.fetchone()

    linked_data = get_linked_data(discord_id)
    if linked_data:
        set_reset_time_default(linked_data[1], *current_data)


# Initiates tracking of all historical stats trackers.
async def start_historical(uuid: str) -> None:
    """
    Initiates historical stat tracking (daily, weekly, etc)
    :param uuid: The uuid of the player's historical stats being initiated
    """
    update_reset_time_default(uuid)
    hypixel_data: dict = await get_hypixel_data(uuid, cache=False)
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
        with sqlite3.connect(f'{REL_PATH}/database/historical.db') as conn:
            cursor = conn.cursor()
            cursor.execute(f"SELECT uuid FROM {tracker} WHERE uuid = '{uuid}'")
            if not cursor.fetchone():
                cursor.execute(f"INSERT INTO {tracker} ({keys}) VALUES ({', '.join('?'*len(stat_keys))})", stat_values)


# Saves historical stats to a new table with a specified name.
# The local stats are subtracted from the current stats leaving
# the gained stats during the historical tracking period.
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

    with sqlite3.connect(f'{REL_PATH}/database/historical.db') as conn:
        cursor = conn.cursor()

        cursor.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name='{table}'")
        if not cursor.fetchone():
            columns = ', '.join([f'{key} INTEGER' for key in stat_keys[1:]])
            cursor.execute(f"CREATE TABLE {table} (uuid TEXT PRIMARY KEY, {columns})")

        cursor.execute(f"SELECT uuid FROM {table} WHERE uuid = '{hypixel_data[0]}'")

        if not cursor.fetchone():
            keys = ', '.join(stat_keys)
            cursor.execute(f"INSERT INTO {table} ({keys}) VALUES ({', '.join('?'*len(stat_keys))})", historical_values)


# Pulls a player's historical stats from the database
def get_historical(uuid: str, table_name: str):
    """
    Returns historical data from a specified table to a specified player
    :param uuid: the uuid of the respective user
    :param table_name: the name of the respective table (daily, weekly, etc)
    """
    with sqlite3.connect(f'{REL_PATH}/database/historical.db') as conn:
        cursor = conn.cursor()

        try:
            cursor.execute(f"SELECT * FROM {table_name} WHERE uuid = '{uuid}'")
            historical_data = cursor.fetchone()
        except sqlite3.OperationalError:
            historical_data = ()

    return historical_data



# Builds invalid lookback embed
def build_invalid_lookback_embeds(max_lookback) -> list:
    """
    Responds to a interaction with an max lookback exceeded message
    :param max_lookback: The maximum lookback the user had availiable
    """
    format_values = {'max_lookback': max_lookback}
    embeds = load_embeds('max_lookback', format_values, color='primary')

    return embeds


# Returns total amount of days back a player's stats can be
# checked based on a primary and secondary discord id.
def get_lookback_eligiblility(discord_id_primary: int, discord_id_secondary: int) -> int:
    """
    Returns the amount of days back a user can check a player's historical stats
    :param discord_id_primary: the primary discord id to use (linked discord account of player)
    :param discord_id_secondary: the secondary discord id to use (the interaction user's id) 
    """
    subscription = None
    if discord_id_primary:
        subscription = get_subscription(discord_id=discord_id_primary)

    if not subscription or not discord_id_primary:
        subscription = get_subscription(discord_id=discord_id_secondary)

    if subscription:
        if 'basic' in subscription[1]:
            return 60
        if 'pro' in subscription[1]:
            return -1
    return 30


async def yearly_eligibility_check(interaction: Interaction,
                             discord_id: int | None) -> bool:
    """
    Checks if a user is able to use yearly stats commands and responds accordingly
    :param interaction: the discord interaction object
    :param discord_id: the discord id of the linked player being checked
    """
    subscription = None
    if discord_id:
        subscription = get_subscription(discord_id=discord_id)

    if not subscription and not get_subscription(interaction.user.id):
        embeds = load_embeds('yearly_eligibility_check', color='primary')
        await interaction.followup.send(embeds=embeds)
        return False
    return True


async def reset_historical(method: str, table_format: str,
                           condition: str, client: Client | None = None):
    """
    Loops through historical and resets each row if a condition is met
    :param method: The historical type (daily, weekly, etc)
    :param table_format: The datetime strftime format for the table name
    :param condition: The condition to be evaluated to determine whether or not to reset
    :param client: discord client object for error logging
    """
    # Get all linked accounts
    with sqlite3.connect(f'{REL_PATH}/database/core.db') as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM linked_accounts')
        row = cursor.fetchone()

        linked_data = {}
        while row:
            linked_data[row[1]] = row[0]
            row = cursor.fetchone()

    # Get all configuration and historical
    with sqlite3.connect(f'{REL_PATH}/database/historical.db') as conn:
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
        if not historical:
            continue

        try:
            uuid = historical[0]
            start_time = time.time()

            gmt_offset, hour = get_reset_time(uuid)

            timezone = utc_now + timedelta(hours=gmt_offset)

            if eval(condition) and timezone.hour == hour:
                hypixel_data = await get_hypixel_data(uuid, cache=True, cache_obj=historic_cache)
                hypixel_data = get_player_dict(hypixel_data)

                stat_keys: list = get_config()['tracked_bedwars_stats']
                stat_values = [hypixel_data.get("achievements", {}).get("bedwars_level", 0)]

                for key in stat_keys:
                    stat_values.append(hypixel_data.get("stats", {}).get("Bedwars", {}).get(key, 0))
                stat_keys.insert(0, 'level')

                with sqlite3.connect(f'{REL_PATH}/database/historical.db') as conn:
                    cursor = conn.cursor()

                    set_clause = ', '.join([f"{column} = ?" for column in stat_keys])
                    cursor.execute(f"UPDATE {method} SET {set_clause} WHERE uuid = '{uuid}'", stat_values)

                stat_values.insert(0, uuid)
                table_name = (timezone - timedelta(days=1)).strftime(table_format)
                save_historical(historical, stat_values, table=table_name)

                time_elapsed = time.time() - start_time
                sleep_time = 2 - (time_elapsed)
                await asyncio.sleep(sleep_time)

        except Exception as error:
            await log_error_msg(client=client, error=error)
            continue


class HistoricalManager:
    def __init__(self, discord_id: int, uuid: str=None):
        self._discord_id = discord_id
        self._uuid = uuid

        self.TIMEZONE = 'timezone'
        self.RESET_HOUR = 'reset_hour'


    def _get_uuid(self):
        if self._uuid:
            return self._uuid

        linked_data = get_linked_data(self._discord_id)
        if linked_data:
            return linked_data[1]

        raise NoLinkedAccountError(
            'Couldn\'t find a linked player associated with the passed discord id!')


    def get_reset_time_configured(self):
        """Attempt to get time configuration data for specified discord id"""
        return get_reset_time_configured(self._discord_id)


    def get_reset_time_default(self, uuid: str=None):
        """Gets the default reset time assigned randomly for a player"""
        if not uuid:
            uuid = self._get_uuid()
        return get_reset_time_default(uuid)


    def get_reset_time(self, uuid: str=None):
        """
        Attempts to get the configured reset time of the discord user\n
        If the discord user has not configured a reset time, the player's default reset time will be used
        :param uuid: The backup uuid if the discord user has no configured reset time
        """
        if not uuid:
            uuid = self._get_uuid()
        return get_reset_time(uuid)


    def update_reset_time_default(self, uuid: str=None):
        """
        Updates a player's default reset time
        :param uuid: The uuid of the relative player
        """
        if not uuid:
            uuid = self._get_uuid()
        update_reset_time_default(uuid)


    def update_reset_time_configured(self, value: int, method: str):
        """
        Updates discord id based reset time configuration
        :param value: the value associated with the method
        :param method: row name (timezone, reset_hour)
        """
        update_reset_time_configured(self._discord_id, value, method)


    async def start_historical(self, uuid: str=None) -> None:
        """
        Initiates historical stat tracking (daily, weekly, etc)
        :param uuid: The uuid of the player's historical stats being initiated
        """
        if not uuid:
            uuid = self._get_uuid()
        await start_historical(uuid)


    def save_historical(self, local_data: tuple, hypixel_data: tuple, table: str) -> None:
        """
        Saves historical data to a specified table, typically used when historical stats reset.
        Creates new table if specified table doesn't exist
        :param local_data: The historical starting data
        :param hypixel_data: The current hypixel data
        :param table: The name of the table to save the historical data to
        """
        save_historical(local_data, hypixel_data, table)


    def get_historical(self, uuid: str=None, table_name: str='daily'):
        """
        Returns historical data from a specified table to a specified player
        :param uuid: the uuid of the respective user
        :param table_name: the name of the respective table (daily, weekly, etc)
        """
        if not uuid:
            uuid = self._get_uuid()
        return get_historical(uuid, table_name)


    def build_invalid_lookback_embeds(self, max_lookback: int) -> list:
        """
        Responds to a interaction with an max lookback exceeded message
        :param max_lookback: The maximum lookback the user had availiable
        """
        return build_invalid_lookback_embeds(max_lookback)


    def get_lookback_eligiblility(self, discord_id_primary: int, discord_id_secondary: int) -> int:
        """
        Returns the amount of days back a user can check a player's historical stats
        :param discord_id_primary: the primary discord id to use (linked discord account of player)
        :param discord_id_secondary: the secondary discord id to use (the interaction user's id) 
        """
        return get_lookback_eligiblility(discord_id_primary, discord_id_secondary)
