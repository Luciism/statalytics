"""Reset time related functionality."""

import random
from abc import abstractmethod, ABC
from dataclasses import dataclass

from ..aliases import PlayerUUID
from ..common import MISSING
from ..db import ensure_cursor, Cursor
from ..accounts.linking import uuid_to_discord_id


@dataclass
class ResetTime:
    """Reset time dataclass."""
    utc_offset: int=MISSING
    """The UTC offset to base the reset time off of."""
    reset_hour: int=MISSING
    """The hour (0-23) to reset rotatational stats at."""
    reset_minute: int=MISSING
    """The minute (0-63) to reset rotational stats at."""

    def as_tuple(self) -> tuple[int, int, int]:
        """A tuple of [utc_offset, reset_hour, reset_minute]"""
        return (self.utc_offset, self.reset_hour, self.reset_minute)

    def as_dict(self) -> dict:
        return {
            "utc_offset": self.utc_offset,
            "reset_hour": self.reset_hour,
            "reset_minute": self.reset_minute
        }


class _ResetTimeManagerBase(ABC):
    """Base class for reset time managers."""
    @staticmethod
    def __random_default_hour() -> int:
        """Default randomly generated reset time value."""
        return random.randint(0, 23)

    @staticmethod
    def __random_default_minute() -> int:
        """Default randomly generated reset time value."""
        return random.choice([0, 15, 30, 45])

    @abstractmethod
    def _select_reset_time_data(
        self, cursor: Cursor, selector: str="*") -> None: ...

    @abstractmethod
    def _update_reset_time_data(
        self, cursor: Cursor, set_clause: str, values: list[int]) -> None: ...

    @abstractmethod
    def _insert_reset_time_data(
        self, cursor: Cursor, timezone: int, reset_hour: int, reset_minute: int
    ) -> None: ...

    @abstractmethod
    def _delete_reset_time_data(self, cursor: Cursor) -> None: ...


    @ensure_cursor
    def update(self, new_value: ResetTime, *, cursor: Cursor=None) -> None:
        """
        Update a users reset time to the given spec.

        :param new_value: The new reset time info to set for the user.
        """
        # Add each to dictionary of values to update
        values_to_update = {}

        # Add values that are set to update dict
        if new_value.utc_offset is not MISSING:
            values_to_update["timezone"] = new_value.utc_offset

        if new_value.reset_hour is not MISSING:
            values_to_update["reset_hour"] = new_value.reset_hour

        if new_value.reset_minute is not MISSING:
            values_to_update["reset_minute"] = new_value.reset_minute


        # Check if data exists
        self._select_reset_time_data(cursor)

        if cursor.fetchone():
            # Empty ResetTime object was passed
            if len(values_to_update) == 0:
                return

            # Update provided values
            set_clause = ", ".join([f"{k} = ?" for k in values_to_update])
            self._update_reset_time_data(
                cursor, set_clause, list(values_to_update.values()))
        else:
            # Insert provided values with default values where data is missing
            self._insert_reset_time_data(
                cursor,
                values_to_update.get("timezone", 0),
                values_to_update.get("reset_hour", self.__random_default_hour()),
                values_to_update.get("reset_minute", self.__random_default_minute())
            )


    @ensure_cursor
    def get(self, *, cursor: Cursor=None) -> ResetTime | None:
        """Get the reset time info of the user."""
        self._select_reset_time_data(
            cursor, selector="timezone, reset_hour, reset_minute")

        result = cursor.fetchone()
        if result is None:
            return None

        return ResetTime(*result)


    @ensure_cursor
    def remove(self, *, cursor: Cursor=None) -> None:
        """Remove the user's reset time data."""
        self._delete_reset_time_data(cursor)


class ConfiguredResetTimeManager(_ResetTimeManagerBase):
    """Reset time manager for configured reset times."""
    def __init__(self, discord_id: int) -> None:
        """
        Initialize the class.

        :param discord_id: The Discord user ID of the respective user.
        """
        self._discord_id = discord_id

    def _select_reset_time_data(
        self, cursor: Cursor, selector: str = "*"
    ) -> None:
        cursor.execute(
            f"SELECT {selector} FROM configured_reset_times WHERE discord_id = ?",
            (self._discord_id,))

    def _update_reset_time_data(
        self, cursor: Cursor, set_clause: str, values: list[int]
    ) -> None:
        cursor.execute(
            f"UPDATE configured_reset_times SET {set_clause} WHERE discord_id = ?",
            (*values, self._discord_id))

    def _insert_reset_time_data(
        self, cursor: Cursor, timezone: int, reset_hour: int, reset_minute: int
    ) -> None:
        cursor.execute(
            "INSERT INTO configured_reset_times "
            "(discord_id, timezone, reset_hour, reset_minute) VALUES (?, ?, ?, ?)",
            (self._discord_id, timezone, reset_hour, reset_minute)
        )

    def _delete_reset_time_data(self, cursor: Cursor) -> None:
        cursor.execute(
            "DELETE FROM configured_reset_times WHERE discord_id = ?",
            (self._discord_id,))


class DefaultResetTimeManager(_ResetTimeManagerBase):
    """Reset time manager for default reset times."""
    def __init__(self, uuid: PlayerUUID) -> None:
        """
        Initialize the class.

        :param uuid: The UUID of the respective player.
        """
        self._player_uuid = uuid

    def _select_reset_time_data(
        self, cursor: Cursor, selector: str = "*"
    ) -> None:
        cursor.execute(
            f"SELECT {selector} FROM default_reset_times WHERE uuid = ?",
            (self._player_uuid,))

    def _update_reset_time_data(
        self, cursor: Cursor, set_clause: str, values: list[int]
    ) -> None:
        cursor.execute(
            f"UPDATE default_reset_times SET {set_clause} WHERE uuid = ?",
            (*values, self._player_uuid))

    def _insert_reset_time_data(
        self, cursor: Cursor, timezone: int, reset_hour: int, reset_minute: int
    ) -> None:
        cursor.execute(
            "INSERT INTO default_reset_times "
            "(uuid, timezone, reset_hour, reset_minute) VALUES (?, ?, ?, ?)",
            (self._player_uuid, timezone, reset_hour, reset_minute)
        )

    def _delete_reset_time_data(self, cursor: Cursor) -> None:
        cursor.execute(
            "DELETE FROM default_reset_times WHERE uuid = ?", (self._player_uuid,))


@ensure_cursor
def get_dynamic_reset_time(
    uuid: PlayerUUID,
    *, cursor: Cursor=None
) -> ResetTime:
    """
    Get a reset time based on the configured reset time of the linked
    player and the default reset time of the player. If a player is linked
    and has a reset time configured, that will be used. Otherwise the player's
    default reset time will be used. If neither is found, it will default to
    `ResetTime(utc_offset=0, reset_hour=0, reset_minute=0)`.

    :param uuid: The UUID of the respective player.
    :return ResetTime: The reset time of the player.
    """
    reset_time = None

    # Attempt to get the user linked to the player
    linked_discord_id = uuid_to_discord_id(uuid)

    # Use the linked users configured reset time if it exists
    if linked_discord_id:
        reset_time = ConfiguredResetTimeManager(linked_discord_id).get(cursor=cursor)

    # Otherwise use the player's default reset time
    if reset_time is None:
        reset_time = DefaultResetTimeManager(uuid).get(cursor=cursor)

    # Return reset time with a default of zero values if it doesn't exist
    return reset_time or ResetTime(0, 0, 0)
