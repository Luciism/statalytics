"""Database respository for live leaderboards."""

from enum import Enum

import aiosqlite

from ...db import AsyncCursor, async_ensure_cursor
from .models import GuildLiveLeaderboard


class SetLiveLbResult(Enum):
    """The outcome of a set live leaderboard database operation."""
    ok = 0
    "Success."
    err_message_conflict = 1
    "Error: the message ID conflicts with another live leaderboard."


class LiveLeaderboardsRepo:
    """Database respository for live leaderboards."""

    @async_ensure_cursor
    @staticmethod
    async def get_live_leaderboard_path(
        message_id: int,
        *,
        cursor: AsyncCursor = None,
    ) -> str | None:
        """
        Get the leaderboard path associated with a live leaderboard's message ID.

        :param message_id: The message ID of the live leaderboard.
        """
        cursor = await cursor.execute(
            "SELECT * FROM live_leaderboards WHERE message_id = ?",
            [message_id],
        )
        live_lb_row = await cursor.fetchone()

        if live_lb_row is None:
            return None

        return live_lb_row["leaderboard_path"]

    @async_ensure_cursor
    @staticmethod
    async def set_live_leaderboard(
        lb: GuildLiveLeaderboard,
        *,
        cursor: AsyncCursor = None,
    ) -> SetLiveLbResult:
        """
        Create or update a live leaderboard.
        An update will modify the channel and message IDs.

        :param lb: The live leaderboard data to set.
        :return SetLiveLbResult: An enum detailing whether the operation succeeded.
        """
        cursor = await cursor.execute(
            "SELECT * FROM live_leaderboards WHERE guild_id = ? AND leaderboard_path = ?",
            [lb.guild_id, lb.leaderboard_path],
        )
        live_lb_row = await cursor.fetchone()

        try:
            if live_lb_row is None:
                _ = await cursor.execute(
                    "INSERT INTO live_leaderboards "
                    + "(guild_id, leaderboard_path, channel_id, message_id) VALUES (?, ?, ?, ?)",
                    [
                        lb.guild_id,
                        lb.leaderboard_path,
                        lb.channel_id,
                        lb.message_id,
                    ],
                )
                return SetLiveLbResult.ok

            _ = await cursor.execute(
                "UPDATE live_leaderboards SET channel_id = ?, message_id = ? "
                + "WHERE guild_id = ? AND leaderboard_path = ?",
                [
                    lb.channel_id,
                    lb.message_id,
                    lb.guild_id,
                    lb.leaderboard_path,
                ],
            )
            return SetLiveLbResult.ok
        except aiosqlite.IntegrityError:
            return SetLiveLbResult.err_message_conflict

    @async_ensure_cursor
    @staticmethod
    async def unset_live_leaderboard(
        guild_id: int,
        leaderboard_path: str,
        *,
        cursor: AsyncCursor = None,
    ) -> GuildLiveLeaderboard | None:
        """
        Delete a live leaderboard from the database.

        :param guild_id: The Discord guild ID associated with the live leaderboard.
        :param leaderboard_path: The leaderboard path of the live leaderboard.
        :return GuildLiveLeaderboard: The live leaderboard that previously existed.
        """
        cursor = await cursor.execute(
            "SELECT * FROM live_leaderboards WHERE guild_id = ? AND leaderboard_path = ?",
            [guild_id, leaderboard_path],
        )
        live_lb_row = await cursor.fetchone()

        if live_lb_row is None:
            return None

        cursor = await cursor.execute(
            "DELETE FROM live_leaderboards WHERE guild_id = ? AND leaderboard_path = ?",
            [guild_id, leaderboard_path],
        )

        return GuildLiveLeaderboard(**dict(live_lb_row))

    @async_ensure_cursor
    @staticmethod
    async def get_all_guild_live_lbs(
        guild_id: int,
        *,
        cursor: AsyncCursor = None,
    ) -> list[GuildLiveLeaderboard]:
        """
        Get all live leaderboards associated with a Discord guild.

        :param guild_id: The ID of the Discord guild.
        """
        cursor = await cursor.execute(
            "SELECT * FROM live_leaderboards WHERE guild_id = ?",
            [guild_id],
        )

        live_lb_rows = await cursor.fetchall()
        return [GuildLiveLeaderboard(**dict(row)) for row in live_lb_rows]

    @async_ensure_cursor
    @staticmethod
    async def get_guild_live_lb(
        guild_id: int,
        leaderboard_path: str,
        *,
        cursor: AsyncCursor = None,
    ) -> GuildLiveLeaderboard | None:
        """
        Get a Discord guild's live leaderboard for a given leaderboard path.
    
        :param guild_id: The ID of the Discord guild.
        :param leaderboard_path: The leaderboard path of the live leaderboard. 
        """
        cursor = await cursor.execute(
            "SELECT * FROM live_leaderboards "
            + "WHERE guild_id = ? AND leaderboard_path = ?",
            [guild_id, leaderboard_path],
        )

        live_lb_row = await cursor.fetchone()
        if live_lb_row is None:
            return None

        return GuildLiveLeaderboard(**dict(live_lb_row))

    @async_ensure_cursor
    @staticmethod
    async def get_all_live_lbs_for_lb_path(
        leaderboard_path: str,
        *,
        cursor: AsyncCursor = None,
    ) -> list[GuildLiveLeaderboard]:
        """
        Get all live leaderboards for a given leaderboard path regardless
        of the Discord guild.

        :param leaderboard_path: The leaderboard path of the live leaderboards.
        """
        cursor = await cursor.execute(
            "SELECT * FROM live_leaderboards WHERE leaderboard_path = ?",
            [leaderboard_path],
        )

        live_lb_rows = await cursor.fetchall()
        return [GuildLiveLeaderboard(**dict(row)) for row in live_lb_rows]
