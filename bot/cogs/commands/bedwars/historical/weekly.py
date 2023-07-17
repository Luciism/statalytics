import asyncio
from datetime import datetime, timedelta, timezone

import discord
from discord import app_commands
from discord.ext import commands, tasks

from render.historical import render_historical
from statalib import (
    HistoricalManager,
    reset_historical,
    fetch_player_info,
    uuid_to_discord_id,
    username_autocompletion,
    generic_command_cooldown,
    fetch_hypixel_data,
    update_command_stats,
    fetch_skin_model,
    ordinal, loading_message,
    handle_modes_renders,
    log_error_msg,
    fname
)


class Weekly(commands.Cog):
    def __init__(self, client):
        self.client: discord.Client = client
        self.LOADING_MSG = loading_message()


    @tasks.loop(hours=1)
    async def reset_weekly(self):
        utc_now = datetime.utcnow()
        if not utc_now.weekday() in (5, 6, 0):
            return

        await reset_historical(
            tracker='weekly',
            period_format='weekly_%Y_%U',
            condition='timezone.weekday() == 6',
            client=self.client
        )


    async def cog_load(self):
        self.reset_weekly.start()


    async def cog_unload(self):
        self.reset_weekly.cancel()


    @reset_weekly.before_loop
    async def before_reset_weekly(self):
        now = datetime.now()
        sleep_seconds = (60 - now.minute) * 60 - now.second
        await asyncio.sleep(sleep_seconds)


    @reset_weekly.error
    async def on_reset_weekly_error(self, error):
        await log_error_msg(self.client, error)


    @app_commands.command(name="weekly", description="View the weekly stats of a player")
    @app_commands.autocomplete(username=username_autocompletion)
    @app_commands.describe(username='The player you want to view')
    @app_commands.checks.dynamic_cooldown(generic_command_cooldown)
    async def weekly(self, interaction: discord.Interaction, username: str=None):
        await interaction.response.defer()

        name, uuid = await fetch_player_info(username, interaction)

        historic = HistoricalManager(interaction.user.id, uuid)
        gmt_offset, hour = historic.get_reset_time()

        historical_data = historic.get_historical(identifier='monthly')

        if not historical_data:
            await historic.start_historical()
            await interaction.followup.send(f'Historical stats for {fname(name)} will now be tracked.')
            return

        await interaction.followup.send(self.LOADING_MSG)
        skin_res = await fetch_skin_model(uuid, 144)
        hypixel_data = await fetch_hypixel_data(uuid)

        now = datetime.now(timezone(timedelta(hours=gmt_offset)))
        formatted_date = now.strftime(f"%b {now.day}{ordinal(now.day)}, %Y")

        next_occurrence = now.replace(hour=hour, minute=0, second=0, microsecond=0)
        while now >= next_occurrence or next_occurrence.weekday() != 6:
            next_occurrence += timedelta(days=1)
        utc_next_occurrence = next_occurrence.astimezone(timezone.utc)
        timestamp = int(utc_next_occurrence.timestamp())

        kwargs = {
            "name": name,
            "uuid": uuid,
            "identifier": "weekly",
            "relative_date": formatted_date,
            "title": "Weekly BW Stats",
            "hypixel_data": hypixel_data,
            "skin_res": skin_res,
            "save_dir": interaction.id
        }

        await handle_modes_renders(
            interaction=interaction,
            func=render_historical,
            kwargs=kwargs,
            message=f':alarm_clock: Resets <t:{timestamp}:R>'
        )
        update_command_stats(interaction.user.id, 'weekly')


    @app_commands.command(name="lastweek", description="View last weeks stats of a player")
    @app_commands.autocomplete(username=username_autocompletion)
    @app_commands.describe(username='The player you want to view', weeks='The lookback amount in weeks')
    @app_commands.checks.dynamic_cooldown(generic_command_cooldown)
    async def lastweek(self, interaction: discord.Interaction, username: str=None, weeks: int=1):
        await interaction.response.defer()
        name, uuid = await fetch_player_info(username, interaction)

        historic = HistoricalManager(interaction.user.id, uuid)
        discord_id = uuid_to_discord_id(uuid=uuid)

        max_lookback = historic.get_lookback_eligiblility(discord_id, interaction.user.id)
        if -1 != max_lookback < (weeks * 7):
            await interaction.followup.send(embeds=historic.build_invalid_lookback_embeds(max_lookback))
            return

        weeks = max(weeks, 1)

        gmt_offset = historic.get_reset_time()[0]

        now = datetime.now(timezone(timedelta(hours=gmt_offset)))

        try:
            relative_date = now - timedelta(weeks=weeks)
            formatted_date = relative_date.strftime("Week %U, %Y")
            period = relative_date.strftime("weekly_%Y_%U")
        except OverflowError:
            await interaction.followup.send('Big, big number... too big number...')
            return

        historical_data = historic.get_historical(identifier=period)

        if not historical_data:
            await interaction.followup.send(f'{fname(name)} has no tracked data for {weeks} week(s) ago!')
            return

        await interaction.followup.send(self.LOADING_MSG)
        skin_res = await fetch_skin_model(uuid, 144)
        hypixel_data = await fetch_hypixel_data(uuid)

        kwargs = {
            "name": name,
            "uuid": uuid,
            "identifier": "lastweek",
            "relative_date": formatted_date,
            "title": f"{weeks} Weeks Ago",
            "period": period,
            "hypixel_data": hypixel_data,
            "skin_res": skin_res,
            "save_dir": interaction.id
        }

        await handle_modes_renders(interaction, render_historical, kwargs)
        update_command_stats(interaction.user.id, 'lastweek')


async def setup(client: commands.Bot) -> None:
    await client.add_cog(Weekly(client))
