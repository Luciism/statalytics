"""Rotational resetting related functionality."""

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
from ..aliases import PlayerUUID, HypixelData
from ..hypixel.leveling import Leveling
from ..cfg import config
from ..db import ensure_cursor, Cursor
from ..accounts.linking import uuid_to_discord_id
from ..accounts.permissions import AccountPermissions


logger = logging.getLogger(__name__)


@ensure_cursor
def has_auto_reset_access(
    uuid: PlayerUUID,
    auto_reset_config: dict | None=None,
    *, cursor: Cursor=None
) -> bool:
    """
    Check if a player has access to rotational auto resetting.

    :param uuid: The UUID of the respective player.
    :param auto_reset_config: A custom auto reset configuration that should be \
        respected, otherwise the configured one will be used.
    :return bool: Whether the player has access to rotational auto resetting.
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

        linked_discord_id = uuid_to_discord_id(uuid, cursor=cursor)
        if linked_discord_id is None and not uuid in uuid_whitelist:
            # Player is linked to any user
            return False

        # uuid is whitelisted or linked discord account has perms
        user_has_access = AccountPermissions(linked_discord_id) \
            .has_access(perm_whitelist, allow_star_perm, cursor=cursor)

        if not user_has_access and not uuid in uuid_whitelist:
            # User has no access and linked player is not whitelisted
            return False

    # All checks succeeded
    return True


class RotationalResetting:
    """Class to manage rotational resetting."""
    def __init__(self, uuid: str) -> None:
        """
        Initialize the rotational resetting class.

        :param uuid: The UUID of the respective player.
        """
        self._player_uuid = uuid


    def __calculate_data_difference(
        self,
        current_rotational_data: BedwarsRotation,
        current_hypixel_data: HypixelData
    ) -> tuple:
        """Calculate the cumulative difference between current and old data."""
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


    @ensure_cursor
    def archive_rotational_data(
        self,
        period_id: HistoricalRotationPeriodID,
        current_hypixel_data: HypixelData,
        *, cursor: Cursor=None
    ) -> str:
        """
        Save currently active rotational data as a historical data snapshot.

        :param period_id: The period ID information for the reset.
        :param current_hypixel_data: The current Hypixel data of the player.
        :return str: A snapshot ID that can be used to identify the data.
        """
        manager = RotationalStatsManager(self._player_uuid)
        current_rotational_data = manager.get_rotational_data(
            period_id.rotation_type, cursor=cursor)

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

        current_xp = current_rotational_data.data.Experience
        current_bedwars_level = Leveling(xp=current_xp).level

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


    @ensure_cursor
    def refresh_rotational_data(
        self,
        rotation_type: RotationType,
        current_hypixel_data: HypixelData,
        *, cursor: Cursor=None
    ) -> None:
        """
        Refresh rotational data by updating the data to the player's current stats.

        :param rotation_type: The type of rotation; daily, weekly, monthly, etc.
        :param current_hypixel_data: The current Hypixel data of the player.
        """
        timestamp = datetime.now(UTC).timestamp()

        # Get snapshot ID
        result = cursor.execute(
            "SELECT snapshot_id FROM rotational_info WHERE uuid = ? "
            "AND rotation = ?", (self._player_uuid, rotation_type.value)
        ).fetchone()

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


@ensure_cursor
def reset_rotational_stats_if_whitelisted(
    uuid: PlayerUUID,
    hypixel_data: HypixelData,
    *, cursor: Cursor=None
) -> None:
    """
    Reset a player's rotational stats if the time since the last
    reset justifies a reset. Should be used every time a request is
    made to hypixel, to ensure that rotational resetting is considered
    manual instead of automatic polling.

    :param uuid: The UUID of the respective player.
    :param hypixel_data: The current Hypixel data of the player.
    """
    # Dont reset players that are auto reset whitelisted
    if has_auto_reset_access(uuid, cursor=cursor):
        return

    now = datetime.now(UTC)
    now_timestamp = now.timestamp()

    # Get last reset timestamp for all rotations
    cursor.execute(
        "SELECT rotation, last_reset_timestamp FROM rotational_info "
        "WHERE uuid = ?", (uuid,))
    last_resets: dict[str, int] = {k: v for k, v in cursor.fetchall()}

    reset_manager = RotationalResetting(uuid)

    def _archive_and_refresh(
        rotation_type: RotationType, dt: datetime, cursor: Cursor
    ) -> None:
        period = HistoricalRotationPeriodID(rotation_type, last_day_dt)
        reset_manager.archive_rotational_data(period, hypixel_data, cursor=cursor)
        reset_manager.refresh_rotational_data(
            rotation_type, hypixel_data, cursor=cursor)

        logger.info(f'(Manual) Reset {rotation_type.value} tracker for: {uuid}')

    if last_resets.get('daily'):
        last_reset = last_resets['daily']

        # Has been more than 1 day since last reset.
        if now_timestamp - last_reset > 86400:
            last_day_dt = now - timedelta(days=1)

            _archive_and_refresh(RotationType.DAILY, last_day_dt, cursor)

    if last_resets.get('weekly'):
        last_reset = last_resets['weekly']

        # Has been more than 7 days since last reset
        if now_timestamp - last_reset > (86400 * 7):
            last_week_dt = now - relativedelta(weeks=1)

            _archive_and_refresh(RotationType.WEEKLY, last_week_dt, cursor)

    if last_resets.get('monthly'):
        last_reset = last_resets['monthly']

        monthly_dt = datetime.fromtimestamp(last_reset, tz=UTC)

        monthly_days = calendar.monthrange(monthly_dt.year, monthly_dt.month)[1]
        monthly_seconds = monthly_days * 86400

        # Has been more than 1 month since last reset
        if now_timestamp - last_reset > monthly_seconds:
            last_month_dt = now - relativedelta(months=1)

            _archive_and_refresh(RotationType.MONTHLY, last_month_dt, cursor)

    if last_resets.get('yearly'):
        last_reset = last_resets['yearly']

        yearly_dt = datetime.fromtimestamp(last_reset, tz=UTC)

        # Regular year length + `True` or `False` for leap year
        yearly_days = 365 + calendar.isleap(yearly_dt.year)
        yearly_seconds = yearly_days * 86400

        # Has been more than 1 year since last reset
        if now_timestamp - last_reset > yearly_seconds:
            last_year_dt = now - relativedelta(years=1)

            _archive_and_refresh(RotationType.YEARLY, last_year_dt, cursor)


# What the fuck?
async def async_reset_rotational_stats_if_whitelisted(
    uuid: PlayerUUID,
    hypixel_data: HypixelData
) -> None:
    """Async wrapper for `~reset_rotational_stats_if_whitelisted()`."""
    reset_rotational_stats_if_whitelisted(uuid, hypixel_data)
