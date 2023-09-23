import sqlite3
import random
import warnings
import calendar
import logging
from datetime import datetime, timedelta, timezone
from dateutil.relativedelta import relativedelta
from typing import Literal

from .errors import NoLinkedAccountError
from .calctools import get_player_dict, get_level
from .linking import get_linked_player, uuid_to_discord_id
from .subscriptions import get_user_property
from .aliases import PlayerUUID
from .permissions import has_access
from .functions import (
    REL_PATH,
    get_config,
    load_embeds
)


warnings.simplefilter('always', DeprecationWarning)
logger = logging.getLogger('statalytics')
logger.setLevel(logging.DEBUG)

TRACKERS = ('daily', 'weekly', 'monthly', 'yearly')
TrackersLiteral = Literal['daily', 'weekly', 'monthly', 'yearly']


def has_auto_reset(
    uuid: PlayerUUID,
    auto_reset_config: dict=None
) -> bool:
    """
    Checks if a player has tracker auto reset permissions
    :param uuid: the player to check for auto reset perms
    :param auto_reset_config: an optional auto reset configuration
    that can be injected, otherwise the one `config.json` will be used
    """
    if auto_reset_config is None:
        auto_reset_config: dict = get_config('tracker_resetting.automatic') or {}

    is_whitelist_only = auto_reset_config.get('whitelist_only')

    if is_whitelist_only:
        uuid_whitelist = auto_reset_config.get('uuid_whitelist', [])
        perm_whitelist = auto_reset_config.get('permission_whitelist', [])
        allow_star_perm = auto_reset_config.get('allow_star_permission', True)

        linked_discord_id = uuid_to_discord_id(uuid)
        if linked_discord_id is None and not uuid in uuid_whitelist:
            return False

        # uuid is whitelisted or linked discord account has perms
        user_has_access = has_access(
            linked_discord_id, perm_whitelist, allow_star_perm)
        if not user_has_access and not uuid in uuid_whitelist:
            return False

    return True



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
async def start_trackers(uuid: PlayerUUID, hypixel_data: dict) -> None:
    """
    Initiates historical stat tracking (daily, weekly, etc)
    :param uuid: The uuid of the player's historical stats being initiated
    :param hypixel_data: the current hypixel data to initalize the trackers with
    """
    update_reset_time_default(uuid)

    hypixel_data = get_player_dict(hypixel_data)

    stat_keys: dict = get_config('tracked_bedwars_stats')
    stat_values = []

    for key in stat_keys:
        stat_values.append(hypixel_data.get("stats", {}).get("Bedwars", {}).get(key, 0))

    keys = ', '.join(stat_keys)
    question_marks = ', '.join('?'*len(stat_keys))

    for tracker in TRACKERS:
        with sqlite3.connect(f'{REL_PATH}/database/core.db') as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT uuid FROM trackers_new WHERE uuid = ? and tracker = ?",
                (uuid, tracker)
            )

            if not cursor.fetchone():
                cursor.execute(
                    f"INSERT INTO trackers_new (uuid, tracker, {keys}) "
                    f"VALUES (?, ?, {question_marks})",
                    (uuid, tracker, *stat_values)
                )


def get_tracker_data(uuid: PlayerUUID, tracker: TrackersLiteral) -> tuple:
    """
    Returns historical data from a specified period for a player
    :param uuid: the uuid of the respective user
    :param tracker: the tracker to get (daily, weekly, etc)
    """
    with sqlite3.connect(f'{REL_PATH}/database/core.db') as conn:
        cursor = conn.cursor()

        cursor.execute(
            f"SELECT * FROM trackers_new WHERE uuid = ? and tracker = ?",
            (uuid, tracker)
        )
        tracker_data = cursor.fetchone()
    return tracker_data


def get_historical_data(uuid: PlayerUUID, period: str) -> tuple:
    """
    Returns historical data from a specified period for a player
    :param uuid: the uuid of the respective user
    :param period: the period of the historical data
    """
    with sqlite3.connect(f'{REL_PATH}/database/core.db') as conn:
        cursor = conn.cursor()

        cursor.execute(
            f"SELECT * FROM historical WHERE uuid = ? and period = ?", (uuid, period))
        historical_data = cursor.fetchone()

    return historical_data


def get_historical(uuid: PlayerUUID, identifier: str, table: str=None):
    """
    **Deprecated** use `get_tracker_data` or `get_historical_data` instead

    Returns historical data from a specified table to a specified player
    :param uuid: the uuid of the respective user
    :param identifier: the column name of the tracker (daily, weekly, etc)
    :param table: the table the data is in (trackers / historical)
    """
    warnings.warn("Use `get_tracker_data` or `get_historical_data`",
                   DeprecationWarning, stacklevel=2)

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
    :param discord_id_primary: the primary discord id to
    use (linked discord account of player)
    :param discord_id_secondary: the secondary
    discord id to use (the interaction user's id)
    """
    max_lookback = None
    if discord_id_primary:
        max_lookback = get_user_property(discord_id_primary, 'max_lookback')

    if not max_lookback or not discord_id_primary:
        max_lookback = get_user_property(discord_id_secondary, 'max_lookback', 30)

    return max_lookback


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

    last_reset_timestamp = datetime.utcnow().timestamp()

    with sqlite3.connect(f'{REL_PATH}/database/core.db') as conn:
        cursor = conn.cursor()

        set_clause = ', '.join([f"{column} = ?" for column in stat_keys])
        cursor.execute(
            "UPDATE trackers_new "
            f"SET last_reset_timestamp = ?, {set_clause} "
            "WHERE uuid = ? and tracker = ?",
            (last_reset_timestamp, *bedwars_data, uuid, tracker)
        )


def save_historical(
    tracker: str,
    bedwars_data: tuple,
    uuid: PlayerUUID,
    current_level: float,
    period: str
) -> tuple:
    """
    Saves historical data to a specified table (used when historical stats reset).
    Creates new table if specified table doesn't exist
    :param tracker_data: the player's bedwars stats at the beginning of the period
    :param bedwars_data: The current bedwars stats of the player
    :param uuid: the uuid of the respective player
    :param current_level: the current level of the player to preserve
    :param period: the time period to save the stats to
    :return: the tracker data that was saved
    """
    tracker_data = get_tracker_data(uuid, tracker)
    if not tracker_data:
        return

    # `uuid, tracker, last_reset_timestamp` onwards
    tracker_data = tracker_data[3:]

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


# This is one long ass function
async def manual_tracker_reset(
    uuid: PlayerUUID,
    hypixel_data: dict
):
    """
    Resets a player's trackers if the time since the last reset
    justifies a reset. Should be used every time a requests is
    made to hypixel so that tracker resetting is considered
    manually instead of automatically polling.
    :param uuid: the uuid of the player to reset trackers of
    :param hypixel_data: the current hypixel data of the player
    """
    # dont reset players that are auto reset whitelisted
    if has_auto_reset(uuid):
        return

    now = datetime.utcnow()
    now_timestamp = now.timestamp()

    last_resets: dict[TrackersLiteral, tuple] = {}

    with sqlite3.connect(f'{REL_PATH}/database/core.db') as conn:
        cursor = conn.cursor()

        # get last reset timestamp for all trackers
        for tracker in TRACKERS:
            cursor.execute(
                'SELECT last_reset_timestamp FROM trackers_new '
                'WHERE uuid = ? and tracker = ?',
                (uuid, tracker))

            last_resets[tracker] = cursor.fetchone()

    hypixel_data = get_player_dict(hypixel_data)
    bedwars_data: dict = hypixel_data.get("stats", {}).get("Bedwars", {})
    bedwars_data_list = bedwars_data_to_tracked_stats_tuple(bedwars_data)

    level = get_level(bedwars_data.get('Experience', 0))

    if last_resets.get('daily'):
        last_reset = last_resets['daily'][0]

        # has been more than 1 day since last reset
        if now_timestamp - last_reset > 86400:
            last_day = now - timedelta(days=1)

            save_historical(
                tracker='daily',
                bedwars_data=bedwars_data_list,
                uuid=uuid,
                current_level=level,
                period=last_day.strftime('daily_%Y_%m_%d')
            )
            await reset_tracker(
                uuid, tracker='daily', bedwars_data=bedwars_data_list)
            logger.info(f'(Manual) Reset daily tracker for: {uuid}')

    if last_resets.get('weekly'):
        last_reset = last_resets['weekly'][0]

        # has been more than 7 days since last reset
        if now_timestamp - last_reset > (86400 * 7):
            last_week = now - relativedelta(weeks=1)

            save_historical(
                tracker='weekly',
                bedwars_data=bedwars_data_list,
                uuid=uuid,
                current_level=level,
                period=last_week.strftime('weekly_%Y_%U')
            )
            await reset_tracker(
                uuid, tracker='weekly', bedwars_data=bedwars_data_list)
            logger.info(f'(Manual) Reset weekly tracker for: {uuid}')

    if last_resets.get('monthly'):
        last_reset = last_resets['monthly'][0]

        monthly_dt = datetime.fromtimestamp(last_reset, tz=timezone.utc)

        monthly_days = calendar.monthrange(monthly_dt.year, monthly_dt.month)[1]
        monthly_seconds = monthly_days * 86400

        # has been more than 1 month since last reset
        if now_timestamp - last_reset > monthly_seconds:
            last_month = now - relativedelta(months=1)

            save_historical(
                tracker='monthly',
                bedwars_data=bedwars_data_list,
                uuid=uuid,
                current_level=level,
                period=last_month.strftime('monthly_%Y_%m')
            )
            await reset_tracker(
                uuid, tracker='monthly', bedwars_data=bedwars_data_list)
            logger.info(f'(Manual) Reset monthly tracker for: {uuid}')

    if last_resets.get('yearly'):
        last_reset = last_resets['yearly'][0]

        yearly_dt = datetime.fromtimestamp(last_reset, tz=timezone.utc)

        # regular year length + `True` or `False` for leap year
        yearly_days = 365 + calendar.isleap(yearly_dt.year)
        yearly_seconds = yearly_days * 86400

        # has been more than 1 year since last reset
        if now_timestamp - last_reset > yearly_seconds:
            last_year = now - relativedelta(years=1)

            save_historical(
                tracker='yearly',
                bedwars_data=bedwars_data_list,
                uuid=uuid,
                current_level=level,
                period=last_year.strftime('yearly_%Y')
            )
            await reset_tracker(
                uuid, tracker='yearly', bedwars_data=bedwars_data_list)
            logger.info(f'(Manual) Reset yearly tracker for: {uuid}')


class HistoricalManager:
    def __init__(self, discord_id: int, uuid: PlayerUUID=None):
        """
        Historical / tracker stats manager
        :param discord_id: the discord id of the user to manage
        :param uuid: override the default player uuid linked to the discord id
        """
        self._discord_id = discord_id
        self._uuid = uuid

        self.TIMEZONE = 'timezone'
        self.RESET_HOUR = 'reset_hour'

        self.refresh()


    def refresh(self):
        """Refresh the class data"""
        # default values are `False` since values could be `None`
        self._configured_timezone = False
        self._configured_reset_hour = False

        self._default_timezone = False
        self._default_reset_hour = False

        self._timezone = False
        self._reset_hour = False


    def _get_uuid(self, safe: bool=False):
        if self._uuid:
            return self._uuid

        uuid = get_linked_player(self._discord_id)
        if uuid:
            return uuid

        if safe:
            raise NoLinkedAccountError(
                "Couldn't find a linked player associated with the passed discord id!")
        return None


    def get_reset_time_configured(self):
        """Attempt to get time configuration data for specified discord id"""
        return get_reset_time_configured(self._discord_id)


    def get_reset_time_default(self, uuid: PlayerUUID=None):
        """Gets the default reset time assigned randomly for a player"""
        if not uuid:
            uuid = self._get_uuid(safe=True)
        return get_reset_time_default(uuid)


    def get_reset_time(self, uuid: PlayerUUID=None):
        """
        Attempts to get the configured reset time of the discord user\n
        If the discord user has not configured a reset time,
        the player's default reset time will be used
        :param uuid: The backup uuid if the discord user has no configured reset time
        """
        if not uuid:
            uuid = self._get_uuid(safe=False)
        return get_reset_time(uuid)


    def update_reset_time_default(self, uuid: PlayerUUID=None):
        """
        Updates a player's default reset time
        :param uuid: The uuid of the relative player
        """
        if not uuid:
            uuid = self._get_uuid(safe=True)
        update_reset_time_default(uuid)


    def update_reset_time_configured(self, value: int, method: str):
        """
        Updates discord id based reset time configuration
        :param value: the value associated with the method
        :param method: row name (timezone, reset_hour)
        """
        update_reset_time_configured(self._discord_id, value, method)


    async def start_trackers(
        self, hypixel_data: dict, uuid: PlayerUUID=None
    ) -> None:
        """
        Initiates historical stat tracking (daily, weekly, etc)
        :param uuid: The uuid of the player's historical stats being initiated
        :param hypixel_data: the current hypixel data to initalize the tracker with
        """
        if not uuid:
            uuid = self._get_uuid(safe=True)
        await start_trackers(uuid, hypixel_data)


    def save_historical(
        self, local_data: tuple, hypixel_data: tuple,
        uuid: PlayerUUID, level: int, period: str
    ) -> None:
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


    def get_tracker_data(
        self, uuid: PlayerUUID=None, tracker: TrackersLiteral='daily'
    ) -> tuple:
        """
        Returns historical data from a specified period for a player
        :param uuid: the uuid of the respective user
        :param tracker: the tracker to get (daily, weekly, etc)
        """
        if not uuid:
            uuid = self._get_uuid(safe=True)
        return get_tracker_data(uuid, tracker)


    def get_historical_data(self, period: str, uuid: PlayerUUID=None) -> tuple:
        """
        Returns historical data from a specified period for a player
        :param uuid: the uuid of the respective user
        :param period: the period of the historical data
        """
        if not uuid:
            uuid = self._get_uuid(safe=True)
        return get_historical_data(uuid, period)


    def get_historical(
        self, uuid: PlayerUUID=None, identifier: str='daily', table: str=None
    ) -> tuple:
        """
        Returns historical data from a specified table to a specified player
        :param uuid: the uuid of the respective user
        :param identifier: the column name of the tracker (daily, weekly, etc)
        :param table: the table the data is in (trackers / historical)
        """
        if not uuid:
            uuid = self._get_uuid(safe=True)
        return get_historical(uuid, identifier, table)


    def build_invalid_lookback_embeds(self, max_lookback: int) -> list:
        """
        Responds to a interaction with an max lookback exceeded message
        :param max_lookback: The maximum lookback the user had availiable
        """
        return build_invalid_lookback_embeds(max_lookback)


    def get_max_lookback(
        self, discord_id_primary: int, discord_id_secondary: int
    ) -> int:
        """
        Returns the amount of days back a user can check a player's historical stats
        :param discord_id_primary: the primary discord id to use (linked discord account of player)
        :param discord_id_secondary: the secondary discord id to use (the interaction user's id)
        """
        return get_max_lookback(discord_id_primary, discord_id_secondary)


    def _set_configured_reset_time(self):
        reset_time = get_reset_time_configured(self._discord_id)

        self._configured_timezone, self._configured_reset_hour\
            = reset_time or (None, None)


    def _set_default_reset_time(self):
        uuid = self._get_uuid(safe=False)

        if uuid:
            reset_time = get_reset_time_default(uuid)

            if reset_time:
                self._default_timezone, self._default_reset_hour = reset_time
                return
        self._default_timezone, self._default_reset_hour = (None, None)


    def _set_reset_time(self):
        # use configured discord bound if it exists
        configured = get_reset_time_configured(self._discord_id)

        if configured is not None:
            self._timezone, self._reset_hour = configured
            return

        # use player bound
        uuid = self._get_uuid(safe=False)

        if uuid:
            reset_time = get_reset_time(uuid)
            if reset_time:
                self._timezone, self._reset_hour = reset_time
                return

        # use fallback
        self._timezone, self._reset_hour = (0, 0)


    @property
    def configured_timezone(self) -> int | None:
        """The configured timezone bound to discord user's discord account"""
        if self._configured_timezone is False:
            self._set_configured_reset_time()
        return self._configured_timezone

    @property
    def configured_reset_hour(self) -> int | None:
        """The configured tracker reset hour bound to discord user's discord account"""
        if self._configured_reset_hour is False:
            self._set_configured_reset_time()
        return self._configured_reset_hour

    @property
    def default_timezone(self) -> int | None:
        """The default timezone bound to discord user's linked minecraft account."""
        if self._default_timezone is False:
            self._set_default_reset_time()
        return self._default_timezone

    @property
    def default_reset_hour(self) -> int | None:
        """The default tracker reset hour bound to
        discord user's linked minecraft account."""
        if self._default_reset_hour is False:
            self._set_default_reset_time()
        return self._default_reset_hour

    @property
    def timezone(self) -> int:
        """
        The dynamically determined timezone of the discord account.

        First it will find and return the user configured discord
        account bound timezone if it exists, otherwise it will return
        the default linked minecraft account bound timezone.

        If there is no linked minecraft account or no default timezone,
        `0` will be returned.
        """
        if self._timezone is False:
            self._set_reset_time()
        return self._timezone

    @property
    def reset_hour(self) -> int:
        """
        The dynamically determined tracker reset hour of the discord account.

        First it will find and return the user configured discord
        account bound reset hour if it exists, otherwise it will return
        the default linked minecraft account bound reset hour.

        If there is no linked minecraft account or no default reset hour,
        `0` will be returned.
        """
        if self._reset_hour is False:
            self._set_reset_time()
        return self._reset_hour
