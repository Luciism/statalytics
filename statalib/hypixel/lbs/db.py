from enum import Enum

import aiosqlite

from ...db import AsyncCursor, async_ensure_cursor
from .models import GuildLiveLeaderboard


class SetLiveLbResult(Enum):
    ok = 0
    err_channel_conflict = 1


class LiveLeaderboardsRepo:
    @async_ensure_cursor
    @staticmethod
    async def get_live_leaderboard_path(
        message_id: int,
        *,
        cursor: AsyncCursor = None,
    ) -> str | None:
        cursor = await cursor.execute(
            "SELECT * FROM live_leaderboards WHERE message_id = ?",
            [message_id],
        )
        lb_channel_row = await cursor.fetchone()

        if lb_channel_row is None:
            return None

        return lb_channel_row["leaderboard_path"]

    @async_ensure_cursor
    @staticmethod
    async def set_live_leaderboard(
        channel: GuildLiveLeaderboard,
        *,
        cursor: AsyncCursor = None,
    ) -> SetLiveLbResult:
        cursor = await cursor.execute(
            "SELECT * FROM live_leaderboards WHERE guild_id = ? AND leaderboard_path = ?",
            [channel.guild_id, channel.leaderboard_path],
        )
        lb_channel_row = await cursor.fetchone()

        try:
            if lb_channel_row is None:
                _ = await cursor.execute(
                    "INSERT INTO live_leaderboards "
                    + "(guild_id, leaderboard_path, channel_id, message_id) VALUES (?, ?, ?, ?)",
                    [
                        channel.guild_id,
                        channel.leaderboard_path,
                        channel.channel_id,
                        channel.message_id,
                    ],
                )
                return SetLiveLbResult.ok

            _ = await cursor.execute(
                "UPDATE live_leaderboards SET channel_id = ?, message_id = ? "
                + "WHERE guild_id = ? AND leaderboard_path = ?",
                [
                    channel.channel_id,
                    channel.message_id,
                    channel.guild_id,
                    channel.leaderboard_path,
                ],
            )
            return SetLiveLbResult.ok
        except aiosqlite.IntegrityError:
            return SetLiveLbResult.err_channel_conflict

    @async_ensure_cursor
    @staticmethod
    async def unset_live_leaderboard(
        guild_id: int,
        leaderboard_path: str,
        *,
        cursor: AsyncCursor = None,
    ) -> GuildLiveLeaderboard | None:
        cursor = await cursor.execute(
            "SELECT * FROM live_leaderboards WHERE guild_id = ? AND leaderboard_path = ?",
            [guild_id, leaderboard_path],
        )
        lb_channel_row = await cursor.fetchone()

        if lb_channel_row is None:
            return None

        cursor = await cursor.execute(
            "DELETE FROM live_leaderboards WHERE guild_id = ? AND leaderboard_path = ?",
            [guild_id, leaderboard_path],
        )

        return GuildLiveLeaderboard(**dict(lb_channel_row))

    @async_ensure_cursor
    @staticmethod
    async def get_all_guild_live_lbs(
        guild_id: int,
        *,
        cursor: AsyncCursor = None,
    ) -> list[GuildLiveLeaderboard]:
        cursor = await cursor.execute(
            "SELECT * FROM live_leaderboards WHERE guild_id = ?",
            [guild_id],
        )

        lb_channel_rows = await cursor.fetchall()
        return [GuildLiveLeaderboard(**dict(row)) for row in lb_channel_rows]

    @async_ensure_cursor
    @staticmethod
    async def get_guild_live_lb(
        guild_id: int,
        leaderboard_path: str,
        *,
        cursor: AsyncCursor = None,
    ) -> GuildLiveLeaderboard | None:
        cursor = await cursor.execute(
            "SELECT * FROM live_leaderboards "
            + "WHERE guild_id = ? AND leaderboard_path = ?",
            [guild_id, leaderboard_path],
        )

        lb_channel_row = await cursor.fetchone()
        if lb_channel_row is None:
            return None

        return GuildLiveLeaderboard(**dict(lb_channel_row))

    @async_ensure_cursor
    @staticmethod
    async def get_all_live_lbs_for_lb_path(
        leaderboard_path: str,
        *,
        cursor: AsyncCursor = None,
    ) -> list[GuildLiveLeaderboard]:
        """ """
        cursor = await cursor.execute(
            "SELECT * FROM live_leaderboards WHERE leaderboard_path = ?",
            [leaderboard_path],
        )

        lb_channel_rows = await cursor.fetchall()
        return [GuildLiveLeaderboard(**dict(row)) for row in lb_channel_rows]
