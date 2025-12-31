import asyncio
import logging
from copy import deepcopy
from datetime import UTC, datetime, timedelta
from typing import final

import discord
import statalib as lib
from discord.ext import commands, tasks
from statalib.hypixel.lbs import LiveLeaderboardsRepo
from statalib.hypixel.lbs.db import GuildLiveLeaderboard
from typing_extensions import override

import helper

logger = logging.getLogger(__name__)

UPDATE_GAP = 60 * 60 * 24  # Seconds


class UpdateLiveLb:
    def __init__(self, leaderboard_path: str, client: helper.Client) -> None:
        self._lb_path: str = leaderboard_path
        self.client: helper.Client = client

    async def _build_embeds_and_files(
        self,
    ) -> tuple[list[discord.Embed], list[discord.File]]:
        return await helper.leaderboards.generate_embeds_for_leaderboard_path(
            self._lb_path
        )

    async def _update_guild_live_lb(
        self,
        live_lb: GuildLiveLeaderboard,
        embeds: list[discord.Embed],
        files: list[discord.File],
        update_dt: datetime,
    ) -> None:
        channel = self.client.get_channel(live_lb.channel_id)

        if not isinstance(channel, discord.TextChannel):
            return

        lb_msg = channel.get_partial_message(live_lb.message_id)

        next_update = update_dt + timedelta(seconds=UPDATE_GAP)
        content = (
            f"Last updated <t:{int(update_dt.timestamp())}:R>\n"
            + f"Next update <t:{int(next_update.timestamp())}:R>"
        )

        try:
            # Make copy of files so that they arent modified by this call
            # in such a case that new a message has to be made.
            _ = await lb_msg.edit(
                content=content, embeds=embeds, attachments=deepcopy(files)
            )
        except discord.errors.NotFound:
            # Create new message
            lb_msg = await channel.send(content=content, embeds=embeds, files=files)

            live_lb.message_id = lb_msg.id
            _ = await LiveLeaderboardsRepo.set_live_leaderboard(live_lb)

    async def update(self) -> None:
        update_dt = datetime.now(UTC)
        embeds, files = await self._build_embeds_and_files()

        live_lbs = await LiveLeaderboardsRepo.get_all_live_lbs_for_lb_path(
            self._lb_path
        )

        for live_lb in live_lbs:
            try:
                await self._update_guild_live_lb(live_lb, embeds, files, update_dt)
            except (
                discord.errors.Forbidden,
                discord.errors.HTTPException,
                discord.errors.NotFound,
            ) as exc:
                logger.error("Failed to update live leaderboard:", exc_info=exc)


@final
class UpdateLiveLeaderboardsCog(commands.Cog):
    def __init__(self, client: helper.Client):
        self.client = client

    @tasks.loop(seconds=UPDATE_GAP)
    async def update_live_leaderboards_loop(self):
        await self.client.wait_until_ready()

        await UpdateLiveLb("bedwars_level", self.client).update()
        await UpdateLiveLb("wins_new", self.client).update()
        await UpdateLiveLb("final_kills_new", self.client).update()

    @update_live_leaderboards_loop.error
    async def on_loop_error(self, error: BaseException):
        if not isinstance(error, Exception):
            return

        await lib.handlers.log_error_msg(self.client, error)
        self.update_live_leaderboards_loop.restart()

    @override
    async def cog_load(self):
        _ = self.update_live_leaderboards_loop.start()

    @override
    async def cog_unload(self):
        self.update_live_leaderboards_loop.cancel()

    @update_live_leaderboards_loop.before_loop
    async def before_update_listings(self):
        # Wait for next day to start
        now = datetime.now(UTC)
        tmr = datetime.now(UTC).replace(
            day=now.day + 1, hour=0, minute=0, second=0, microsecond=0
        )

        delta = tmr - now
        await asyncio.sleep(delta.total_seconds())


async def setup(client: helper.Client) -> None:
    await client.add_cog(UpdateLiveLeaderboardsCog(client))
