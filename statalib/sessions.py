"""Session stats related functionality."""

import logging
from datetime import UTC, datetime
from uuid import uuid4

from .aliases import BedwarsData, HypixelData, PlayerUUID
from .db import Cursor, ensure_cursor
from .errors import DataNotFoundError
from .stats_snapshot import BedwarsStatsSnapshot, update_snapshot_data


class BedwarsSession:
    """Represents a Bedwars session."""

    def __init__(self, session_info: dict, session_data: BedwarsStatsSnapshot) -> None:
        self.data = session_data

        self.player_uuid: str = session_info["uuid"]
        self.session_id: int = session_info["session"]
        self.creation_timestamp: int = session_info["creation_timestamp"]


class SessionManager:
    """Bedwars session manager class."""

    def __init__(self, uuid: PlayerUUID) -> None:
        self._uuid = uuid

    @ensure_cursor
    def get_session(
        self, session_id: int | None = 1, *, cursor: Cursor = None
    ) -> BedwarsSession | None:
        """
        Get a session with a specific ID.

        :param session_id: The ID of the session to retrieve. If left as `None`, \
            an existing session with the lowest ID will be returned.
        """
        # Select session info
        if session_id is None:
            # Use lowest session
            cursor.execute(
                "SELECT * FROM session_info WHERE uuid = ? ORDER BY session ASC",
                (self._uuid,),
            )
        else:
            # Use specified session
            cursor.execute(
                "SELECT * FROM session_info WHERE uuid = ? AND session = ?",
                (self._uuid, session_id),
            )

        session_info = cursor.fetchone()

        if session_info is None:
            return None

        # Convert session info to dictionary
        column_names = [col[0] for col in cursor.description]
        session_info_dict = dict(zip(column_names, session_info))

        # Select session stats
        snapshot_id = session_info_dict["snapshot_id"]
        cursor.execute(
            "SELECT * FROM bedwars_stats_snapshots WHERE snapshot_id = ?",
            (snapshot_id,),
        )
        session_data: tuple | None = cursor.fetchone()

        if session_data is None:
            raise DataNotFoundError(
                f"Snapshot data missing for snapshot ID '{snapshot_id}'"
            )

        session_snapshot_data = BedwarsStatsSnapshot(*session_data)
        return BedwarsSession(session_info_dict, session_data=session_snapshot_data)

    @ensure_cursor
    def create_session(
        self, session_id: int, hypixel_data: HypixelData, *, cursor: Cursor = None
    ) -> None:
        """
        Create a new bedwars session using the provided hypixel data.

        :param session_id: The ID of the session to be created.
        :param hypixel_data: The hypixel data to create the session with.
        """
        hypixel_bedwars_data: BedwarsData = (
            (hypixel_data.get("player") or {}).get("stats", {}).get("Bedwars", {})
        )

        # Create dictionary of session data
        session_data = {
            k: hypixel_bedwars_data.get(k, 0) for k in BedwarsStatsSnapshot.keys(False)
        }
        snapshot = BedwarsStatsSnapshot(snapshot_id=uuid4().hex, **session_data)

        self.create_session_from_snapshot(session_id, snapshot, cursor=cursor)

    @ensure_cursor
    def create_session_from_snapshot(
        self, session_id: int, snapshot: BedwarsStatsSnapshot, *, cursor: Cursor = None
    ) -> None:
        """
        Create a new bedwars session using the provided Bedwars stats snapshot.

        :param session_id: The ID of the session to be created.
        :param snapshot: The snapshot to create the session with.
        """
        # Generate timestamp and session snapshot id
        timestamp = datetime.now(UTC).timestamp()

        # Insert session info
        _ = cursor.execute(
            """
            INSERT INTO session_info
            (session, uuid, snapshot_id, creation_timestamp)
            VALUES (?, ?, ?, ?)
        """,
            (session_id, self._uuid, snapshot.snapshot_id, timestamp),
        )

        # Insert session data
        column_names = ", ".join(snapshot.keys())
        question_marks = ", ".join("?" * len(snapshot.keys()))
        _ = cursor.execute(
            f"""
            INSERT INTO bedwars_stats_snapshots
            ({column_names}) VALUES ({question_marks})
        """,
            snapshot.as_tuple(),
        )

    @ensure_cursor
    def update_session_snapshot(
        self, session_id: int, snapshot: BedwarsStatsSnapshot, *, cursor: Cursor = None
    ) -> None:
        """
        Update an existing bedwars session using the provided Bedwars stats snapshot.

        :param session_id: The ID of the session to be updated.
        :param snapshot: The snapshot to update the session with.
        """
        session_info = cursor.execute(
            "SELECT * FROM session_info WHERE session = ? AND uuid = ?", (session_id, self._uuid)
        ).fetchone()

        if session_info is None:
            return
    
        snapshot.snapshot_id = session_info[2]
        update_snapshot_data(snapshot, cursor=cursor)

    @ensure_cursor
    def delete_session(self, session_id: int, *, cursor: Cursor = None) -> None:
        """
        Delete a session with a specific ID.

        :param session_id: The ID of the user's session to be deleted.
        """
        # Get snapshot ID
        result = cursor.execute(
            "SELECT snapshot_id FROM session_info WHERE session = ? AND uuid = ?",
            (session_id, self._uuid),
        ).fetchone()

        if result is None:
            raise DataNotFoundError(
                f"Session '{session_id}' not found for player '{self._uuid}'"
            )

        snapshot_id = result[0]

        cursor.execute(
            "DELETE FROM bedwars_stats_snapshots WHERE snapshot_id = ?", (snapshot_id,)
        )
        cursor.execute("DELETE FROM session_info WHERE snapshot_id = ?", (snapshot_id,))

    @ensure_cursor
    def session_count(self, *, cursor: Cursor = None) -> int:
        """
        Return the total amount of sessions the user has active.

        :param cursor: A custom `sqlite3.Cursor` object to operate on.
        """
        # Get snapshot ID
        cursor.execute(
            "SELECT COUNT(*) FROM session_info WHERE uuid = ?", (self._uuid,)
        )
        result = cursor.fetchone()

        if result is None:
            return 0
        return result[0]

    @ensure_cursor
    def active_sessions(self, *, cursor: Cursor = None) -> list[int]:
        """
        Return a list of session IDs of the user's active sessions.

        :param cursor: A custom `sqlite3.Cursor` object to operate on.
        """
        results = cursor.execute(
            "SELECT session FROM session_info WHERE uuid = ? ORDER BY session ASC",
            (self._uuid,),
        ).fetchall()

        return [res[0] for res in results]
