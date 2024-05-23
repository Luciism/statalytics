import sqlite3
from datetime import datetime, UTC
from uuid import uuid4

from .calctools import get_player_dict
from .aliases import PlayerUUID
from .common import REL_PATH
from .stats_snapshot import BedwarsStatsSnapshot


class BedwarsSession:
    def __init__(self, session_info: dict, session_data: BedwarsStatsSnapshot) -> None:
        self.data = session_data

        self.player_uuid: str = session_info["uuid"]
        self.session_id: int = session_info["session"]
        self.creation_timestamp: int = session_info["creation_timestamp"]


class SessionManager:
    def __init__(self, uuid: PlayerUUID) -> None:
        self._uuid = uuid


    def get_session(self, session_id: int | None=1) -> BedwarsSession | None:
        """
        Get a session with a specific ID.
        :param session_id: The ID of the session to retrieve. If left as `None`, \
            an existing session with the lowest ID will be returned.
        """
        with sqlite3.connect(f'{REL_PATH}/database/core.db') as conn:
            cursor = conn.cursor()

            # Select session info
            if session_id is None:
                # Use lowest session
                cursor.execute(
                    "SELECT * FROM sessions WHERE uuid = ? ORDER BY session ASC", (self._uuid,))
            else:
                # Use specified session
                cursor.execute(
                    "SELECT * FROM sessions WHERE uuid = ? AND session = ?",
                    (self._uuid, session_id))

            session_info = cursor.fetchone()

            if session_info is None:
                return None

            # Convert session info to dictionary
            column_names = [col[0] for col in cursor.description]
            session_info_dict = dict(zip(column_names, session_info))

            # Select session stats
            snapshot_id = session_info_dict["snapshot_id"]
            cursor.execute(
                "SELECT * FROM bedwars_stats_snapshots WHERE snapshot_id = ?", (snapshot_id,))
            session_data: tuple | None = cursor.fetchone()

            if session_data is None:
                # Raise snapshot data missing error instead
                raise NotImplementedError("Data missing")

            session_snapshot_data = BedwarsStatsSnapshot(*session_data)
            return BedwarsSession(session_info_dict, session_data=session_snapshot_data)



    def create_session(self, session_id: int, hypixel_data: dict) -> None:
        """
        Create a new bedwars session using the provided hypixel data.
        :param session_id: The ID of the session to be created.
        :param hypixel_data: The hypixel data to create the session with.
        """
        hypixel_data = get_player_dict(hypixel_data)
        bedwars_stats_data: dict = hypixel_data.get("stats", {}).get("Bedwars", {})

        # Create dictionary of session data
        session_data = {
            k:bedwars_stats_data.get(k, 0)
            for k in BedwarsStatsSnapshot.keys()
        }

        # Generate timestamp and session snapshot id
        timestamp = datetime.now(UTC).timestamp()
        snapshot_id = uuid4().hex

        with sqlite3.connect(f'{REL_PATH}/database/core.db') as conn:
            cursor = conn.cursor()

            # Insert session info
            cursor.execute("""
                INSERT INTO sessions
                (session, uuid, snapshot_id, creation_timestamp)
                VALUES (?, ?, ?, ?)
            """, (session_id, self._uuid, snapshot_id, timestamp))

            # Insert session data
            column_names = ", ".join(session_data.keys())
            question_marks = ", ".join("?"*len(session_data.keys()))
            cursor.execute(f"""
                INSERT INTO bedwars_stats_snapshots
                (snapshot_id, {column_names}) VALUES (?, {question_marks})
            """, (snapshot_id, *session_data.values()))


    def delete_session(self, session_id: int) -> None:
        """
        Delete a session with a specific ID.
        :param session_id: The ID of the user's session to be deleted.
        """
        with sqlite3.connect(f'{REL_PATH}/database/core.db') as conn:
            cursor = conn.cursor()

            # Get snapshot ID
            cursor.execute(
                "SELECT snapshot_id FROM sessions WHERE session = ?", (session_id,))
            result = cursor.fetchone()

            if result is None:
                # Raise custom session not found exception
                raise NotImplementedError("Session not found!")

            snapshot_id = result[0]

            cursor.execute(
                "DELETE FROM bedwars_stats_snapshots WHERE snapshot_id = ?", (snapshot_id,))

            cursor.execute(
                "DELETE FROM sessions WHERE snapshot_id = ?", (snapshot_id,))


    def session_count(self, cursor: sqlite3.Cursor | None=None) -> int:
        """
        Return the total amount of sessions the user has active.
        :param cursor: Optional `sqlite3.Cursor` object to execute on.
        """
        def __session_count(cursor: sqlite3.Cursor) -> int:
            # Get snapshot ID
            cursor.execute(
                "SELECT COUNT(*) FROM sessions WHERE uuid = ?", (self._uuid,))
            result = cursor.fetchone()

            if result is None:
                return 0
            return result[0]

        if cursor:
            return __session_count(cursor)

        with sqlite3.connect(f'{REL_PATH}/database/core.db') as conn:
            return __session_count(conn.cursor())


    def active_sessions(self, cursor: sqlite3.Cursor | None=None) -> list[int]:
        """
        Return a list of session IDs of the user's active sessions.
        :param cursor: Optional `sqlite3.Cursor` object to execute on.
        """
        def __active_sessions(cursor: sqlite3.Cursor) -> list[int]:
            cursor.execute(
                "SELECT session FROM sessions WHERE uuid = ? ORDER BY session ASC",
                (self._uuid,))
            results = cursor.fetchall()

            return [res[0] for res in results]

        if cursor:
            return __active_sessions(cursor)

        with sqlite3.connect(f'{REL_PATH}/database/core.db') as conn:
            return __active_sessions(conn.cursor())
