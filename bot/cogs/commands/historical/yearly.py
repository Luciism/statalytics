import os
import sqlite3
import asyncio

from datetime import datetime, timedelta, timezone
from dateutil.relativedelta import relativedelta

import discord
from discord import app_commands
from discord.ext import commands, tasks

from render.historical import render_historical
from helper.functions import (
    username_autocompletion,
    get_command_cooldown,
    get_hypixel_data,
    update_command_stats,
    authenticate_user,
    start_historical,
    yearly_eligibility,
    uuid_to_discord_id,
    get_time_config,
    fetch_skin_model,
    get_lookback_eligiblility,
    message_invalid_lookback,
    ordinal, loading_message,
    send_generic_renders,
    reset_historical,
    log_error_msg
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
            condition='timezone.timetuple().tm_yday == 1'
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
        try: name, uuid = await authenticate_user(username, interaction)
        except TypeError: return
        refined = name.replace("_", "\_")

        discord_id = uuid_to_discord_id(uuid=uuid)
        gmt_offset, hour = get_time_config(discord_id=discord_id)

        with sqlite3.connect('./database/historical.db') as conn:
            cursor = conn.cursor()
            cursor.execute(f"SELECT uuid FROM yearly WHERE uuid = '{uuid}'")
            historical_data = cursor.fetchone()

        if not historical_data:
            await start_historical(uuid=uuid)
            await interaction.followup.send(f'Historical stats for {refined} will now be tracked.')
            return

        result = await yearly_eligibility(interaction, discord_id)
        if not result:
            return

        await interaction.followup.send(self.LOADING_MSG)
        os.makedirs(f'./database/activerenders/{interaction.id}')
        skin_res = await fetch_skin_model(uuid, 144)
        hypixel_data = await get_hypixel_data(uuid)

        now = datetime.now(timezone(timedelta(hours=gmt_offset)))
        relative_date = now.strftime(f"%b {now.day}{ordinal(now.day)}, %Y")

        if hour > 0: hour -= 1
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
        try: name, uuid = await authenticate_user(username, interaction)
        except TypeError: return

        refined = name.replace("_", "\_")
        discord_id = uuid_to_discord_id(uuid)

        # Check if user is allowed to use command
        result = await yearly_eligibility(interaction, discord_id)
        if not result:
            return

        # Check if user is within their lookback limitations
        max_lookback = await get_lookback_eligiblility(interaction=interaction, discord_id=discord_id)
        if max_lookback == 60 and years == 1:
            pass
        elif -1 != max_lookback < (years * 365):
            await message_invalid_lookback(interaction=interaction, max_lookback=max_lookback)
            return
        if years < 1:
            years = 1

        # Get time / date information
        gmt_offset = get_time_config(discord_id=discord_id)[0]

        now = datetime.now(timezone(timedelta(hours=gmt_offset)))
        relative_date = now - relativedelta(years=years)
        formatted_date = relative_date.strftime("Year %Y")
        try:
            table_name = relative_date.strftime("yearly_%Y")
        except ValueError:
            await interaction.followup.send('Big, big number... too big number...')
            return

        # Check if historical data exists
        with sqlite3.connect('./database/historical.db') as conn:
            cursor = conn.cursor()
            try:
                cursor.execute(f"SELECT uuid FROM {table_name} WHERE uuid = '{uuid}'")
                historical_data = cursor.fetchone()
            except sqlite3.OperationalError:
                historical_data = ()

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
