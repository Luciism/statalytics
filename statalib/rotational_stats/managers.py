"""Functionality for managing rotational stats."""

import sqlite3
from datetime import datetime, UTC
from typing import Callable
from uuid import uuid4

from ._types import RotationType, BedwarsRotation, BedwarsHistoricalRotation
from ._utils import get_bedwars_data
from .reset_time import DefaultResetTimeManager, ResetTime
from ..aliases import PlayerUUID, HypixelData
from ..db import db_connect
from ..stats_snapshot import BedwarsStatsSnapshot, get_snapshot_data


class RotationalStatsManager:
    """Manager for rotational / historical stats."""
    def __init__(self, uuid: PlayerUUID):
        """
        Initialize the rotational stats manager.

        :param discord_id: The Discord user ID of the respective user.
        :param uuid: Override the default player UUID linked to the Discord user.
        """
        self._uuid = uuid


    def __get_rotation_data(
        self,
        exec_select_query: Callable[[sqlite3.Cursor], None]
    ) -> tuple[dict, BedwarsStatsSnapshot] | None:
        """Execute rotational data select query."""
        with db_connect() as conn:
            cursor = conn.cursor()

            exec_select_query(cursor)  # Select query

            rotational_info = cursor.fetchone()
            if rotational_info is None:
                return None

            return get_snapshot_data(cursor, rotational_info)


    def get_rotational_data(
        self,
        rotation_type: RotationType
    ) -> BedwarsRotation | None:
        """
        Get the current rotational data for a player using the specified rotation type.

        :param rotation_type: The type of rotation; daily, weekly, monthly, etc.
        :return BedwarsRotation | None: The rotational data if it exists, \
            otherwise None.
        """
        exec_select_query = lambda cursor: cursor.execute(
            "SELECT * FROM rotational_info WHERE uuid = ? AND rotation = ?",
            (self._uuid, rotation_type.value)
        )

        result = self.__get_rotation_data(exec_select_query)
        if result is None:
            return None  # No data

        return BedwarsRotation(*result)


    def get_historical_rotation_data(
        self,
        period_id: str
    ) -> BedwarsHistoricalRotation | None:
        """
        Get past rotational data for a player using the specified period_id ID type.

        :param period_id: A string that identifies the rotation period.
        :return BedwarsHistoricalRotation | None: The historical rotational data \
            if it exists, otherwise None.
        """
        exec_select_query = lambda cursor: cursor.execute(
            "SELECT * FROM historical_info WHERE uuid = ? AND period_id = ?",
            (self._uuid, period_id)
        )

        result = self.__get_rotation_data(exec_select_query)
        if result is None:
            return None  # No data

        return BedwarsHistoricalRotation(*result)


    def initialize_rotational_tracking(
        self,
        current_hypixel_data: HypixelData
    ) -> None:
        """
        Initialize rotational stats tracking for a player.

        :param current_hypixel_data: The current Hypixel data of the player.
        """
        # Ensure default reset time for the player is set
        DefaultResetTimeManager(self._uuid).update(ResetTime())

        current_bedwars_data = get_bedwars_data(current_hypixel_data)

        # Add tracked rotation data to list
        bedwars_data_list = [
            current_bedwars_data.get(key, 0)
            for key in BedwarsStatsSnapshot.keys(include_snapshot_id=False)
        ]

        # Generate set clause
        stat_keys = BedwarsStatsSnapshot.keys(include_snapshot_id=False)

        set_clause = ", ".join(stat_keys)
        question_marks = ", ".join("?"*len(stat_keys))

        timestamp = datetime.now(UTC).timestamp()

        with db_connect() as conn:
            cursor = conn.cursor()

            for rotation in RotationType:
                # Insert rotational info data
                snapshot_id = uuid4().hex

                cursor.execute(
                    "INSERT INTO rotational_info (uuid, rotation, last_reset_timestamp, "
                    "snapshot_id) VALUES (?, ?, ?, ?)",
                    (self._uuid, rotation.value, timestamp, snapshot_id)
                )

                # Insert snapshot data
                cursor.execute(
                    f"INSERT INTO bedwars_stats_snapshots (snapshot_id, {set_clause}) VALUES (?, {question_marks})",
                    (snapshot_id, *bedwars_data_list)
                )
