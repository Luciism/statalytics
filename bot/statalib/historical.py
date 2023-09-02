import sqlite3
import random

from discord import Interaction

from .errors import NoLinkedAccountError
from .calctools import get_player_dict
from .linking import get_linked_player, uuid_to_discord_id
from .network import fetch_hypixel_data
from .subscriptions import get_subscription
from .aliases import PlayerUUID
from .functions import (
    REL_PATH,
    get_config,
    load_embeds
)


TRACKERS = ('daily', 'weekly', 'monthly', 'yearly')


# Used to get player bound reset times that are assigned automatically.
def get_reset_time_default(uuid: PlayerUUID) -> tuple | None:
    """
    Gets the default reset time assigned randomly for a player
    :param uuid: The uuid of the relative player
    """
    with sqlite3.connect(f'{REL_PATH}/database/core.db') as conn:
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
    with sqlite3.connect(f'{REL_PATH}/database/core.db') as conn:
        cursor = conn.cursor()

        cursor.execute(
            f"SELECT * FROM configured_reset_times WHERE discord_id = {discord_id}")
        configuration_data = cursor.fetchone()

    if configuration_data:
        return configuration_data[1:3]


# Uses both default & configured approaches to getting reset time.
# Configured reset time takes priority and if it doesn't exist
# default reset times will be used. If neither are present
# a reset time of midnight at GMT+0 will be used (0, 0).
def get_reset_time(uuid: PlayerUUID) -> tuple[int, int]:
    """
    Attempts to get the configured reset time of the discord user\n
    If the discord user has not configured a reset time, the player's
    default reset time will be used
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
def set_reset_time_default(uuid: PlayerUUID, timezone: int, reset_hour: int):
    """
    Sets default reset time in historical database (player bound)
    :param uuid: The uuid of the relative player
    :param timezone: The GMT offset to insert
    :param reset_hour: The reset hour to insert
    """
    with sqlite3.connect(f'{REL_PATH}/database/core.db') as conn:
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
def update_reset_time_default(uuid: PlayerUUID):
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
    with sqlite3.connect(f'{REL_PATH}/database/core.db') as conn:
        cursor = conn.cursor()
        cursor.execute(
            f'SELECT timezone FROM configured_reset_times WHERE discord_id = {discord_id}')

        if cursor.fetchone():
            cursor.execute(
                'UPDATE configured_reset_times '
                f'SET {method} = ? '
                'WHERE discord_id = ?',
                (value, discord_id)
            )
        else:
            values = (discord_id, value, 0) if method == 'timezone' else (discord_id, 0, value)
            cursor.execute(
                'INSERT INTO configured_reset_times '
                '(discord_id, timezone, reset_hour) '
                'VALUES (?, ?, ?)', values)

        cursor.execute(
            'SELECT timezone, reset_hour '
            'FROM configured_reset_times '
            'WHERE discord_id = ?',
            (discord_id,))
        current_data = cursor.fetchone()

    uuid = get_linked_player(discord_id)
    if uuid:
        set_reset_time_default(uuid, *current_data)


# Initiates tracking of all historical stats trackers.
async def start_trackers(uuid: PlayerUUID) -> None:
    """
    Initiates historical stat tracking (daily, weekly, etc)
    :param uuid: The uuid of the player's historical stats being initiated
    """
    update_reset_time_default(uuid)

    hypixel_data: dict = await fetch_hypixel_data(uuid, cache=False)
    hypixel_data = get_player_dict(hypixel_data)

    stat_keys: dict = get_config()['tracked_bedwars_stats']
    stat_values = []

    for key in stat_keys:
        stat_values.append(hypixel_data.get("stats", {}).get("Bedwars", {}).get(key, 0))

    keys = ', '.join(stat_keys)
    question_marks = ', '.join('?'*len(stat_keys))

    for tracker in TRACKERS:
        with sqlite3.connect(f'{REL_PATH}/database/core.db') as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT uuid FROM trackers WHERE uuid = ? and tracker = ?", (uuid, tracker))
            if not cursor.fetchone():
                cursor.execute(
                    f"INSERT INTO trackers (uuid, tracker, {keys}) VALUES (?, ?, {question_marks})",
                    (uuid, tracker, *stat_values)
                )


# Pulls a player's historical stats from the database
def get_historical(uuid: PlayerUUID, identifier: str, table: str=None):
    """
    Returns historical data from a specified table to a specified player
    :param uuid: the uuid of the respective user
    :param identifier: the column name of the tracker (daily, weekly, etc)
    :param table: the table the data is in (trackers / historical)
    """
    if not table:
        table = 'trackers' if identifier in TRACKERS else 'historical'
    col = 'tracker' if table == 'trackers' else 'period'

    with sqlite3.connect(f'{REL_PATH}/database/core.db') as conn:
        cursor = conn.cursor()
        try:
            cursor.execute(
                f"SELECT * FROM {table} WHERE uuid = ? and {col} = ?", (uuid, identifier))
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
def get_max_lookback(
    discord_id_primary: int,
    discord_id_secondary: int
) -> int:
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
        if 'basic' in subscription:
            return 60
        if 'pro' in subscription:
            return -1
    return 30


async def yearly_eligibility_check(
    interaction: Interaction,
    discord_id: int | None
) -> bool:
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


def bedwars_data_to_tracked_stats_tuple(
    bedwars_data: dict,
    stat_keys: list=None
):
    """
    Converts a bedwars data dictionary into a tuple of tracked stats
    :param bedwars_data: the bedwars data to convert
    :param stat_keys: a list of keys to use
    im sorry, im too tired to write any better documentation
    """
    if stat_keys is None:
        stat_keys: list = get_config('tracked_bedwars_stats')

    stat_values = []
    for key in stat_keys:
        stat_values.append(bedwars_data.get(key, 0))

    return stat_values


async def reset_tracker(
    uuid: PlayerUUID,
    tracker: str,
    bedwars_data: tuple
):
    """
    Resets a specified tracker by overriding the current data with fresh data
    :param uuid: the uuid of the player to reset the tracker for
    :param tracker: the name of the tracker to reset (daily, weekly, etc)
    :param bedwars_data: the current bedwars stats of the player
    :return: the saved bedwars data as a tuple
    """
    stat_keys: list = get_config('tracked_bedwars_stats')

    with sqlite3.connect(f'{REL_PATH}/database/core.db') as conn:
        cursor = conn.cursor()

        set_clause = ', '.join([f"{column} = ?" for column in stat_keys])
        cursor.execute(
            f"UPDATE trackers SET {set_clause} WHERE uuid = ? and tracker = ?",
            (*bedwars_data, uuid, tracker)
        )


def save_historical(
    tracker: str,
    bedwars_data: tuple,
    uuid: PlayerUUID,
    current_level: float,
    period: str
):
    """
    Saves historical data to a specified table (used when historical stats reset).
    Creates new table if specified table doesn't exist
    :param tracker_data: the player's bedwars stats at the beginning of the period
    :param bedwars_data: The current bedwars stats of the player
    :param uuid: the uuid of the respective player
    :param current_level: the current level of the player to preserve
    :param period: the time period to save the stats to
    """
    tracker_data = get_historical(uuid, tracker)
    if not tracker_data:
        return

    tracker_data = tracker_data[2:]  # uuid, tracker onwards

    stat_keys = get_config('tracked_bedwars_stats')
    stat_values = []

    for value1, value2 in zip(bedwars_data, tracker_data):
        stat_values.append(value1 - value2)

    stat_columns = ', '.join(stat_keys)
    question_marks = ', '.join('?'*len(stat_keys))

    with sqlite3.connect(f'{REL_PATH}/database/core.db') as conn:
        cursor = conn.cursor()

        cursor.execute(
            "SELECT uuid FROM historical WHERE uuid = ? and period = ?", (uuid, period))

        if not cursor.fetchone():
            cursor.execute(f"""
                INSERT INTO historical (uuid, period, level, {stat_columns})
                VALUES (?, ?, ?, {question_marks})""",
                (uuid, period, current_level, *stat_values)
            )

    return tracker_data



class HistoricalManager:
    def __init__(self, discord_id: int, uuid: PlayerUUID=None):
        self._discord_id = discord_id
        self._uuid = uuid

        self.TIMEZONE = 'timezone'
        self.RESET_HOUR = 'reset_hour'


    def _get_uuid(self):
        if self._uuid:
            return self._uuid

        uuid = get_linked_player(self._discord_id)
        if uuid:
            return uuid

        raise NoLinkedAccountError(
            "Couldn't find a linked player associated with the passed discord id!")


    def get_reset_time_configured(self):
        """Attempt to get time configuration data for specified discord id"""
        return get_reset_time_configured(self._discord_id)


    def get_reset_time_default(self, uuid: PlayerUUID=None):
        """Gets the default reset time assigned randomly for a player"""
        if not uuid:
            uuid = self._get_uuid()
        return get_reset_time_default(uuid)


    def get_reset_time(self, uuid: PlayerUUID=None):
        """
        Attempts to get the configured reset time of the discord user\n
        If the discord user has not configured a reset time,
        the player's default reset time will be used
        :param uuid: The backup uuid if the discord user has no configured reset time
        """
        if not uuid:
            uuid = self._get_uuid()
        return get_reset_time(uuid)


    def update_reset_time_default(self, uuid: PlayerUUID=None):
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


    async def start_trackers(self, uuid: PlayerUUID=None) -> None:
        """
        Initiates historical stat tracking (daily, weekly, etc)
        :param uuid: The uuid of the player's historical stats being initiated
        """
        if not uuid:
            uuid = self._get_uuid()
        await start_trackers(uuid)


    def save_historical(self, local_data: tuple, hypixel_data: tuple,
                        uuid: PlayerUUID, level: int, period: str) -> None:
        """
        Saves historical data to a specified table, typically used when historical stats reset.
        Creates new table if specified table doesn't exist
        :param local_data: the player's bedwars stats at the beginning of the period
        :param hypixel_data: The current bedwars stats of the player
        :param uuid: the uuid of the respective player
        :param level: the current level of the player to preserve
        :param period: the time period to save the stats to
        """
        save_historical(local_data, hypixel_data, uuid, level, period)


    def get_historical(self, uuid: PlayerUUID=None, identifier: str='daily',
                       table: str=None) -> tuple:
        """
        Returns historical data from a specified table to a specified player
        :param uuid: the uuid of the respective user
        :param identifier: the column name of the tracker (daily, weekly, etc)
        :param table: the table the data is in (trackers / historical)
        """
        if not uuid:
            uuid = self._get_uuid()
        return get_historical(uuid, identifier, table)


    def build_invalid_lookback_embeds(self, max_lookback: int) -> list:
        """
        Responds to a interaction with an max lookback exceeded message
        :param max_lookback: The maximum lookback the user had availiable
        """
        return build_invalid_lookback_embeds(max_lookback)


    def get_max_lookback(self, discord_id_primary: int,
                         discord_id_secondary: int) -> int:
        """
        Returns the amount of days back a user can check a player's historical stats
        :param discord_id_primary: the primary discord id to use (linked discord account of player)
        :param discord_id_secondary: the secondary discord id to use (the interaction user's id)
        """
        return get_max_lookback(discord_id_primary, discord_id_secondary)
