import random
import sqlite3
from abc import abstractmethod, ABC
from dataclasses import dataclass

from ..aliases import PlayerUUID
from ..common import MISSING
from ..functions import db_connect
from ..linking import uuid_to_discord_id


@dataclass
class ResetTime:
    utc_offset: int=MISSING
    reset_hour: int=MISSING


class _ResetTimeManagerBase(ABC):
    @staticmethod
    def __gen_default() -> int:
        """Default randomly generated reset time value."""
        return random.randint(0, 23)

    @abstractmethod
    def _select_reset_time_data(
        self, cursor: sqlite3.Cursor, selector: str="*") -> None: ...

    @abstractmethod
    def _update_reset_time_data(
        self, cursor: sqlite3.Cursor, set_query: str, values: list[int]) -> None: ...

    @abstractmethod
    def _insert_reset_time_data(
        self, cursor: sqlite3.Cursor, timezone: int, reset_hour: int) -> None: ...

    @abstractmethod
    def _delete_reset_time_data(self, cursor: sqlite3.Cursor) -> None: ...


    def update(self, new_value: ResetTime) -> None:
        """
        Update a users reset time to the given spec
        :param new_value: The new reset time info to set for the user.
        """
        # Add each to dictionary of values to update
        values_to_update = {}

        if new_value.utc_offset is not MISSING:
            values_to_update["timezone"] = new_value.utc_offset

        if new_value.reset_hour is not MISSING:
            values_to_update["reset_hour"] = new_value.reset_hour

        with db_connect() as conn:
            cursor = conn.cursor()

            # Check if data exists
            self._select_reset_time_data(cursor)

            if cursor.fetchone():
                # Empty ResetTime object was passed
                if len(values_to_update) == 0:
                    return

                # Update provided values
                set_query = ", ".join([f"{k} = ?" for k in values_to_update])
                self._update_reset_time_data(
                    cursor, set_query, list(values_to_update.values()))
            else:
                # Insert provided values with random values where data is missing
                self._insert_reset_time_data(
                    cursor,
                    values_to_update.get("timezone", 0),
                    values_to_update.get("reset_hour", self.__gen_default())
                )


    def get(self) -> ResetTime | None:
        """Return the reset time info of the user."""
        with db_connect() as conn:
            cursor = conn.cursor()

            self._select_reset_time_data(cursor, selector="timezone, reset_hour")

            result = cursor.fetchone()
            if result is None:
                return None

            return ResetTime(*result)


    def remove(self) -> None:
        """Remove the users reset time data."""
        with db_connect() as conn:
            self._delete_reset_time_data(conn.cursor())


class ConfiguredResetTimeManager(_ResetTimeManagerBase):
    def __init__(self, discord_id: int) -> None:
        self._discord_id = discord_id

    def _select_reset_time_data(
        self, cursor: sqlite3.Cursor, selector: str = "*"
    ) -> None:
        cursor.execute(
            f"SELECT {selector} FROM configured_reset_times WHERE discord_id = ?",
            (self._discord_id,))

    def _update_reset_time_data(
        self, cursor: sqlite3.Cursor, set_query: str, values: list[int]
    ) -> None:
        cursor.execute(
            f"UPDATE configured_reset_times SET {set_query} WHERE discord_id = ?",
            (*values, self._discord_id))

    def _insert_reset_time_data(
        self, cursor: sqlite3.Cursor, timezone: int, reset_hour: int
    ) -> None:
        cursor.execute(
            "INSERT INTO configured_reset_times (discord_id, timezone, reset_hour) "
            "VALUES (?, ?, ?)", (self._discord_id, timezone, reset_hour)
        )

    def _delete_reset_time_data(self, cursor: sqlite3.Cursor) -> None:
        cursor.execute(
            "DELETE FROM configured_reset_times WHERE discord_id = ?",
            (self._discord_id,))


class DefaultResetTimeManager(_ResetTimeManagerBase):
    def __init__(self, uuid: PlayerUUID) -> None:
        self._player_uuid = uuid

    def _select_reset_time_data(
        self, cursor: sqlite3.Cursor, selector: str = "*"
    ) -> None:
        cursor.execute(
            f"SELECT {selector} FROM default_reset_times WHERE uuid = ?",
            (self._player_uuid,))

    def _update_reset_time_data(
        self, cursor: sqlite3.Cursor, set_query: str, values: list[int]
    ) -> None:
        cursor.execute(
            f"UPDATE default_reset_times SET {set_query} WHERE uuid = ?",
            (*values, self._player_uuid))

    def _insert_reset_time_data(
        self, cursor: sqlite3.Cursor, timezone: int, reset_hour: int
    ) -> None:
        cursor.execute(
            "INSERT INTO default_reset_times (uuid, timezone, reset_hour) "
            "VALUES (?, ?, ?)", (self._player_uuid, timezone, reset_hour)
        )

    def _delete_reset_time_data(self, cursor: sqlite3.Cursor) -> None:
        cursor.execute(
            "DELETE FROM default_reset_times WHERE uuid = ?", (self._player_uuid,))


def get_dynamic_reset_time(uuid: PlayerUUID) -> ResetTime:
    """
    Return a reset time based on the configured reset time of the linked
    player and the default reset time of the player. If a player is linked
    and has a reset time configured, that will be used. Otherwise the player's
    default reset time will be used. If neither is found, it will default to
    `ResetTime(utc_offset=0, reset_hour=0)`

    :param uuid: The uuid of the respective player.
    """
    reset_time = None

    # Attempt to get the user linked to the player
    linked_discord_id = uuid_to_discord_id(uuid)

    # Use the linked users configured reset time if it exists
    if linked_discord_id:
        reset_time = ConfiguredResetTimeManager(linked_discord_id).get()

    # Otherwise use the player's default reset time
    if reset_time is None:
        reset_time = DefaultResetTimeManager(uuid).get()

    # Return reset time with a default of zero values if it doesn't exist
    return reset_time or ResetTime(0, 0)
