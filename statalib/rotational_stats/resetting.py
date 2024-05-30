import logging
import calendar
from datetime import UTC, datetime, timedelta
from dateutil.relativedelta import relativedelta
from uuid import uuid4

from statalib.errors import DataNotFoundError
from statalib.stats_snapshot import BedwarsStatsSnapshot
from ._types import (
    HistoricalRotationPeriodID,
    BedwarsRotation,
    RotationType
)
from ._utils import get_bedwars_data
from .managers import RotationalStatsManager
from ..aliases import PlayerUUID
from ..calctools.utils import get_level
from ..cfg import config
from ..functions import db_connect
from ..linking import uuid_to_discord_id
from ..permissions import has_access


logger = logging.getLogger(__name__)


def has_auto_reset_access(
    uuid: PlayerUUID,
    auto_reset_config: dict | None=None
) -> bool:
    """
    Checks if a player has tracker auto reset permissions
    :param uuid: the player to check for auto reset perms
    :param auto_reset_config: an optional auto reset configuration
    that can be injected, otherwise the one `config.json` will be used
    """
    # Use config from config file
    if auto_reset_config is None:
        auto_reset_config: dict = config('apps.bot.tracker_resetting.automatic') or {}

    is_whitelist_only = auto_reset_config.get('whitelist_only')

    # User must be whitelisted to have auto reset
    if is_whitelist_only:
        uuid_whitelist = auto_reset_config.get('uuid_whitelist', [])
        perm_whitelist = auto_reset_config.get('permission_whitelist', [])
        allow_star_perm = auto_reset_config.get('allow_star_permission', True)

        linked_discord_id = uuid_to_discord_id(uuid)
        if linked_discord_id is None and not uuid in uuid_whitelist:
            # Player is linked to any user
            return False

        # uuid is whitelisted or linked discord account has perms
        user_has_access = has_access(
            linked_discord_id, perm_whitelist, allow_star_perm)
        if not user_has_access and not uuid in uuid_whitelist:
            # User has no access and linked player is not whitelisted
            return False

    # All checks succeeded
    return True


class RotationalResetting:
    def __init__(self, uuid: str) -> None:
        self._player_uuid = uuid


    def __calculate_data_difference(
        self,
        current_rotational_data: BedwarsRotation,
        current_hypixel_data: dict
    ) -> tuple:
        # Get player bedwars data
        current_bedwars_data = get_bedwars_data(current_hypixel_data)

        rotational_data_dict = current_rotational_data.data.as_dict(
            include_snapshot_id=False)

        # Map required data
        current_bedwars_data_filtered = {
            k: current_bedwars_data.get(k, 0) for k in rotational_data_dict.keys()
        }

        # Calculate the differnce between current and old
        calculated_values = [
            current - old  # Difference
            for current, old
            in zip(current_bedwars_data_filtered.values(), rotational_data_dict.values())
        ]

        return calculated_values


    def archive_rotational_data(
        self,
        period_id: HistoricalRotationPeriodID,
        current_hypixel_data: dict,
    ) -> str:
        """
        Save currently active rotational data as a historical data snapshot.

        :param period_id: The period ID information for the reset
        :param current_hypixel_data: The current hypixel data of the player.
        :return: The snapshot ID to identify the data.
        """
        manager = RotationalStatsManager(self._player_uuid)
        current_rotational_data = manager.get_rotational_data(period_id.rotation_type)

        # Data was expected
        if current_rotational_data is None:
            raise DataNotFoundError(
                f"No rotational data for rotational type {period_id.rotation_type.value} "
                f"exists for player with UUID {self._player_uuid}"
            )

        calculated_values = self.__calculate_data_difference(
            current_rotational_data, current_hypixel_data)

        # Misc values
        snapshot_id = uuid4().hex
        current_bedwars_level = get_level(current_rotational_data.data.Experience)

        with db_connect() as conn:
            cursor = conn.cursor()

            # Insert info
            cursor.execute(
                "INSERT INTO historical_info (uuid, period_id, level, snapshot_id) "
                "VALUES (?, ?, ?, ?)",
                (self._player_uuid, period_id.to_string(), current_bedwars_level, snapshot_id)
            )

            # Insert data
            keys = BedwarsStatsSnapshot.keys(include_snapshot_id=False)
            column_names = ", ".join(keys)
            question_marks = ", ".join("?"*len(keys))

            cursor.execute(f"""
                INSERT INTO bedwars_stats_snapshots
                (snapshot_id, {column_names}) VALUES (?, {question_marks})
            """, (snapshot_id, *calculated_values))

        return snapshot_id


    def refresh_rotational_data(
        self,
        rotation_type: RotationType,
        current_hypixel_data: dict
    ) -> None:
        """
        Refresh rotational data by updating the data to the current player stats.

        :param rotation_type: The type of rotation; daily, weekly, monthly, etc.
        :param current_hypixel_data: The current hypixel data of the player.
        """
        timestamp = datetime.now(UTC).timestamp()

        with db_connect() as conn:
            cursor = conn.cursor()

            # Get snapshot ID
            cursor.execute(
                "SELECT snapshot_id FROM rotational_info WHERE uuid = ? "
                "AND rotation = ?", (self._player_uuid, rotation_type.value))
            result = cursor.fetchone()

            if result is None:
                return None  # Probably raise an exception instead

            # Update last reset timestamp
            cursor.execute(
                "UPDATE rotational_info SET last_reset_timestamp = ? "
                "WHERE uuid = ? AND rotation = ?",
                (timestamp, self._player_uuid, rotation_type.value)
            )

            snapshot_id = result[0]

            # Convert bedwars data to list of tracked values
            current_bedwars_data = get_bedwars_data(current_hypixel_data)

            bedwars_data_list = [
                current_bedwars_data.get(key, 0)
                for key in BedwarsStatsSnapshot.keys(include_snapshot_id=False)
            ]

            # Format set query
            set_keys = [
                f"{key} = ?"
                for key in BedwarsStatsSnapshot.keys(include_snapshot_id=False)
            ]
            set_clause = ", ".join(set_keys)

            # Update snapshot data
            cursor.execute(
                f"UPDATE bedwars_stats_snapshots SET {set_clause} WHERE snapshot_id = ?",
                (*bedwars_data_list, snapshot_id)
            )


def reset_rotational_stats_if_whitelisted(
    uuid: PlayerUUID,
    hypixel_data: dict
) -> None:
    """
    Resets a player's rotational stats if the time since the last
    reset justifies a reset. Should be used every time a requests is
    made to hypixel so that rotational resetting is considered
    manual instead of automatic polling.

    :param uuid: The uuid of the player to reset the rotational stats of.
    :param hypixel_data: The current hypixel data of the player.
    """
    # Dont reset players that are auto reset whitelisted
    if has_auto_reset_access(uuid):
        return

    now = datetime.now(UTC)
    now_timestamp = now.timestamp()

    with db_connect() as conn:
        cursor = conn.cursor()

        # Get last reset timestamp for all rotations
        cursor.execute(
            "SELECT rotation, last_reset_timestamp FROM rotational_info "
            "WHERE uuid = ?", (uuid,))
        last_resets: dict[str, int] = {k: v for k, v in cursor.fetchall()}

    reset_manager = RotationalResetting(uuid)

    if last_resets.get('daily'):
        last_reset = last_resets['daily']

        # Has been more than 1 day since last reset.
        if now_timestamp - last_reset > 86400:
            last_day_dt = now - timedelta(days=1)

            period = HistoricalRotationPeriodID(RotationType.DAILY, last_day_dt)
            reset_manager.archive_rotational_data(period, hypixel_data)
            reset_manager.refresh_rotational_data(RotationType.DAILY, hypixel_data)

            logger.info(f'(Manual) Reset daily tracker for: {uuid}')

    if last_resets.get('weekly'):
        last_reset = last_resets['weekly']

        # Has been more than 7 days since last reset
        if now_timestamp - last_reset > (86400 * 7):
            last_week_dt = now - relativedelta(weeks=1)

            period = HistoricalRotationPeriodID(RotationType.WEEKLY, last_week_dt)
            reset_manager.archive_rotational_data(period, hypixel_data)
            reset_manager.refresh_rotational_data(RotationType.WEEKLY, hypixel_data)

            logger.info(f'(Manual) Reset weekly tracker for: {uuid}')

    if last_resets.get('monthly'):
        last_reset = last_resets['monthly']

        monthly_dt = datetime.fromtimestamp(last_reset, tz=UTC)

        monthly_days = calendar.monthrange(monthly_dt.year, monthly_dt.month)[1]
        monthly_seconds = monthly_days * 86400

        # Has been more than 1 month since last reset
        if now_timestamp - last_reset > monthly_seconds:
            last_month_dt = now - relativedelta(months=1)

            period = HistoricalRotationPeriodID(RotationType.MONTHLY, last_month_dt)
            reset_manager.archive_rotational_data(period, hypixel_data)
            reset_manager.refresh_rotational_data(RotationType.MONTHLY, hypixel_data)

            logger.info(f'(Manual) Reset monthly tracker for: {uuid}')

    if last_resets.get('yearly'):
        last_reset = last_resets['yearly']

        yearly_dt = datetime.fromtimestamp(last_reset, tz=UTC)

        # Regular year length + `True` or `False` for leap year
        yearly_days = 365 + calendar.isleap(yearly_dt.year)
        yearly_seconds = yearly_days * 86400

        # Has been more than 1 year since last reset
        if now_timestamp - last_reset > yearly_seconds:
            last_year_dt = now - relativedelta(years=1)

            period = HistoricalRotationPeriodID(RotationType.YEARLY, last_year_dt)
            reset_manager.archive_rotational_data(period, hypixel_data)
            reset_manager.refresh_rotational_data(RotationType.YEARLY, hypixel_data)

            logger.info(f'(Manual) Reset yearly tracker for: {uuid}')


async def async_reset_rotational_stats_if_whitelisted(
    uuid: PlayerUUID,
    hypixel_data: dict
) -> None:
    """Async wrapper for ~reset_rotational_stats_if_whitelisted()"""
    reset_rotational_stats_if_whitelisted(uuid, hypixel_data)
