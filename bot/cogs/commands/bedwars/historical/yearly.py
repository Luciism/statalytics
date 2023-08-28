import asyncio
from datetime import datetime, timedelta, timezone
from dateutil.relativedelta import relativedelta

import discord
from discord import app_commands
from discord.ext import commands

from render.historical import render_historical
from statalib import (
    HistoricalManager,
    fetch_player_info,
    uuid_to_discord_id,
    username_autocompletion,
    generic_command_cooldown,
    fetch_hypixel_data,
    update_command_stats,
    yearly_eligibility_check,
    fetch_skin_model,
    ordinal, loading_message,
    handle_modes_renders,
    fname,
    pluralize
)


class Yearly(commands.Cog):
    def __init__(self, client):
        self.client: commands.Bot = client
        self.LOADING_MSG = loading_message()


    @app_commands.command(
        name="yearly",
        description="View the yearly stats of a player")
    @app_commands.describe(player='The player you want to view')
    @app_commands.autocomplete(player=username_autocompletion)
    @app_commands.checks.dynamic_cooldown(generic_command_cooldown)
    async def yearly(self, interaction: discord.Interaction, player: str=None):
        await interaction.response.defer()

        name, uuid = await fetch_player_info(player, interaction)

        historic = HistoricalManager(interaction.user.id, uuid)
        gmt_offset, hour = historic.get_reset_time()

        historical_data = historic.get_historical(identifier='yearly')

        if not historical_data:
            await historic.start_historical()
            await interaction.followup.send(
                f'Historical stats for {fname(name)} will now be tracked.')
            return

        discord_id = uuid_to_discord_id(uuid=uuid)
        result = await yearly_eligibility_check(interaction, discord_id)
        if not result:
            return

        await interaction.followup.send(self.LOADING_MSG)

        skin_model, hypixel_data = await asyncio.gather(
            fetch_skin_model(uuid, 144),
            fetch_hypixel_data(uuid)
        )

        now = datetime.now(timezone(timedelta(hours=gmt_offset)))
        relative_date = now.strftime(f"%b {now.day}{ordinal(now.day)}, %Y")

        if hour > 0:
            hour -= 1

        next_occurrence = datetime(
            year=now.year + 1,
            month=1,
            day=1,
            hour=hour,
            minute=0,
            second=0,
            tzinfo=timezone(timedelta(hours=gmt_offset))
        )

        utc_next_occurrence = next_occurrence.astimezone(timezone.utc)
        timestamp = int(utc_next_occurrence.timestamp())

        kwargs = {
            "name": name,
            "uuid": uuid,
            "identifier": "yearly",
            "relative_date": relative_date,
            "title": "Yearly Stats",
            "hypixel_data": hypixel_data,
            "skin_model": skin_model,
            "save_dir": interaction.id
        }

        await handle_modes_renders(
            interaction=interaction,
            func=render_historical,
            kwargs=kwargs,
            message=f':alarm_clock: Resets <t:{timestamp}:R>'
        )

        update_command_stats(interaction.user.id, 'yearly')


    @app_commands.command(
        name="lastyear",
        description="View last years stats of a player")
    @app_commands.describe(
        player='The player you want to view',
        years='The lookback amount in years')
    @app_commands.autocomplete(player=username_autocompletion)
    @app_commands.checks.dynamic_cooldown(generic_command_cooldown)
    async def lastyear(self, interaction: discord.Interaction,
                       player: str=None, years: int=1):
        await interaction.response.defer()
        name, uuid = await fetch_player_info(player, interaction)

        historic = HistoricalManager(interaction.user.id, uuid)
        discord_id = uuid_to_discord_id(uuid=uuid)

        # Check if user is allowed to use command
        result = await yearly_eligibility_check(interaction, discord_id)
        if not result:
            return

        # Check if user is within their lookback limitations
        # First checks if a user is checking 1 year back with a basic plan
        # and then checks if the max lookback days are within the given amount
        max_lookback = historic.get_max_lookback(discord_id, interaction.user.id)
        if not (max_lookback == 60 and years == 1) and -1 != max_lookback < (years * 365):
            embeds = historic.build_invalid_lookback_embeds(max_lookback)
            await interaction.followup.send(embeds=embeds)
            return

        years = max(years, 1)

        # Get time / date information
        gmt_offset = historic.get_reset_time()[0]

        now = datetime.now(timezone(timedelta(hours=gmt_offset)))
        try:
            relative_date = now - relativedelta(years=years)
            formatted_date = relative_date.strftime("Year %Y")
            period = relative_date.strftime("yearly_%Y")
        except ValueError:
            await interaction.followup.send('Big, big number... too big number...')
            return

        # Check if historical data exists
        historical_data = historic.get_historical(identifier=period)

        if not historical_data:
            await interaction.followup.send(
                f'{fname(name)} has no tracked data for {years} year(s) ago!')
            return

        # Render and send
        await interaction.followup.send(self.LOADING_MSG)

        skin_model, hypixel_data = await asyncio.gather(
            fetch_skin_model(uuid, 144),
            fetch_hypixel_data(uuid)
        )

        kwargs = {
            "name": name,
            "uuid": uuid,
            "identifier": "lastyear",
            "relative_date": formatted_date,
            "title": f"{years} {pluralize(years, 'Year')} Ago",
            "period": period,
            "hypixel_data": hypixel_data,
            "skin_model": skin_model,
            "save_dir": interaction.id,
        }

        await handle_modes_renders(interaction, render_historical, kwargs)
        update_command_stats(interaction.user.id, 'lastyear')


async def setup(client: commands.Bot) -> None:
    await client.add_cog(Yearly(client))
