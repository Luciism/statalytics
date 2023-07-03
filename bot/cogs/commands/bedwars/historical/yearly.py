import os
import asyncio

from datetime import datetime, timedelta, timezone
from dateutil.relativedelta import relativedelta

import discord
from discord import app_commands
from discord.ext import commands, tasks

from render.historical import render_historical
from helper.historical import reset_historical, HistoricalManager
from helper.linking import fetch_player_info, uuid_to_discord_id
from helper.functions import (
    username_autocompletion,
    get_command_cooldown,
    get_hypixel_data,
    update_command_stats,
    yearly_eligibility,
    fetch_skin_model,
    ordinal, loading_message,
    send_generic_renders,
    log_error_msg,
)


class Yearly(commands.Cog):
    def __init__(self, client):
        self.client: discord.Client = client
        self.LOADING_MSG = loading_message()

    @tasks.loop(hours=1)
    async def reset_yearly(self):
        utc_now = datetime.utcnow()
        if not utc_now.timetuple().tm_yday in (1, 2, 365, 366):
            return
        
        await reset_historical(
            method='yearly',
            table_format='yearly_%Y',
            condition='timezone.timetuple().tm_yday == 1',
            client=self.client
        )


    def cog_load(self):
        self.reset_yearly.start()


    def cog_unload(self):
        self.reset_yearly.cancel()


    @reset_yearly.before_loop
    async def before_reset_yearly(self):
        now = datetime.now()
        sleep_seconds = (60 - now.minute) * 60 - now.second
        await asyncio.sleep(sleep_seconds)


    @reset_yearly.error
    async def on_reset_yearly_error(self, error):
        await log_error_msg(self.client, error)


    @app_commands.command(name="yearly", description="View the yearly stats of a player")
    @app_commands.autocomplete(username=username_autocompletion)
    @app_commands.describe(username='The player you want to view')
    @app_commands.checks.dynamic_cooldown(get_command_cooldown)
    async def yearly(self, interaction: discord.Interaction, username: str=None):
        await interaction.response.defer()

        name, uuid = await fetch_player_info(username, interaction)
        refined = name.replace("_", "\_")

        historic = HistoricalManager(interaction.user.id, uuid)
        gmt_offset, hour = historic.get_reset_time()

        historical_data = historic.get_historical(table_name='monthly')

        if not historical_data:
            await historic.start_historical()
            await interaction.followup.send(f'Historical stats for {refined} will now be tracked.')
            return

        discord_id = uuid_to_discord_id(uuid=uuid)
        result = await yearly_eligibility(interaction, discord_id)
        if not result:
            return

        await interaction.followup.send(self.LOADING_MSG)
        os.makedirs(f'./database/activerenders/{interaction.id}')
        skin_res = await fetch_skin_model(uuid, 144)
        hypixel_data = await get_hypixel_data(uuid)

        now = datetime.now(timezone(timedelta(hours=gmt_offset)))
        relative_date = now.strftime(f"%b {now.day}{ordinal(now.day)}, %Y")

        if hour > 0:
            hour -= 1
        next_occurrence = datetime(now.year + 1, 1, 1, hour, 0, 0, tzinfo=timezone(timedelta(hours=gmt_offset)))
        utc_next_occurrence = next_occurrence.astimezone(timezone.utc)
        timestamp = int(utc_next_occurrence.timestamp())

        kwargs = {
            "name": name,
            "uuid": uuid,
            "method": "yearly",
            "relative_date": relative_date,
            "title": "Yearly BW Stats",
            "hypixel_data": hypixel_data,
            "skin_res": skin_res,
            "save_dir": interaction.id
        }

        await send_generic_renders(
            interaction=interaction,
            func=render_historical,
            kwargs=kwargs, 
            message=f':alarm_clock: Resets <t:{timestamp}:R>'
        )

        update_command_stats(interaction.user.id, 'yearly')


    @app_commands.command(name="lastyear", description="View last years stats of a player")
    @app_commands.autocomplete(username=username_autocompletion)
    @app_commands.describe(username='The player you want to view', years='The lookback amount in years')
    @app_commands.checks.dynamic_cooldown(get_command_cooldown)
    async def lastyear(self, interaction: discord.Interaction, username: str=None, years: int=1):
        await interaction.response.defer()
        name, uuid = await fetch_player_info(username, interaction)

        refined = name.replace("_", "\_")

        historic = HistoricalManager(interaction.user.id, uuid)
        
        discord_id = uuid_to_discord_id(uuid=uuid)

        # Check if user is allowed to use command
        result = await yearly_eligibility(interaction, discord_id)
        if not result:
            return
 
        # Check if user is within their lookback limitations
        # First checks if a user is checking 1 year back with a basic plan
        # and then checks if the max lookback days are within the given amount of 
        max_lookback = historic.get_lookback_eligiblility(discord_id, interaction.user.id)
        if not (max_lookback == 60 and years == 1) and -1 != max_lookback < (years * 365):
            await interaction.followup.send(embed=historic.build_invalid_lookback_embed(max_lookback))
            return

        if years < 1:
            years = 1

        # Get time / date information
        gmt_offset = historic.get_reset_time()[0]

        now = datetime.now(timezone(timedelta(hours=gmt_offset)))
        try:
            relative_date = now - relativedelta(years=years)
            formatted_date = relative_date.strftime("Year %Y")
            table_name = relative_date.strftime("yearly_%Y")
        except ValueError:
            await interaction.followup.send('Big, big number... too big number...')
            return

        # Check if historical data exists
        historical_data = historic.get_historical(table_name=table_name)

        if not historical_data:
            await interaction.followup.send(f'{refined} has no tracked data for {years} year(s) ago!')
            return

        # Render and send
        await interaction.followup.send(self.LOADING_MSG)
        os.makedirs(f'./database/activerenders/{interaction.id}')
        skin_res = await fetch_skin_model(uuid, 144)
        hypixel_data = await get_hypixel_data(uuid)

        kwargs = {
            "name": name,
            "uuid": uuid,
            "method": "lastyear",
            "relative_date": formatted_date,
            "title": f"{years} Years Ago",
            "table_name": table_name,
            "hypixel_data": hypixel_data,
            "skin_res": skin_res,
            "save_dir": interaction.id,
        }

        await send_generic_renders(interaction, render_historical, kwargs)
        update_command_stats(interaction.user.id, 'lastyear')


async def setup(client: commands.Bot) -> None:
    await client.add_cog(Yearly(client))
