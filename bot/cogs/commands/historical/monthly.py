import os
import sqlite3
import asyncio

from calendar import monthrange
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
    log_error_msg,
    uuid_to_discord_id,
    get_time_config,
    fetch_skin_model,
    get_lookback_eligiblility,
    message_invalid_lookback,
    ordinal, loading_message,
    send_generic_renders,
    reset_historical
)


class Monthly(commands.Cog):
    def __init__(self, client):
        self.client: discord.Client = client
        self.LOADING_MSG = loading_message()


    @tasks.loop(hours=1)
    async def reset_monthly(self):
        utc_now = datetime.utcnow()
        if not utc_now.day in (1, 2) and not utc_now.day == monthrange(utc_now.year, utc_now.month)[1]:
            return
        
        reset_historical(
            method='monthly',
            table_format='monthly_%Y_%m',
            condition='timezone.day == 1'
        )


    def cog_load(self):
        self.reset_monthly.start()


    def cog_unload(self):
        self.reset_monthly.cancel()


    @reset_monthly.before_loop
    async def before_reset_monthly(self):
        now = datetime.now()
        sleep_seconds = (60 - now.minute) * 60 - now.second
        await asyncio.sleep(sleep_seconds)


    @reset_monthly.error
    async def on_reset_monthly_error(self, error):
        await log_error_msg(self.client, error)


    @app_commands.command(name="monthly", description="View the monthly stats of a player")
    @app_commands.autocomplete(username=username_autocompletion)
    @app_commands.describe(username='The player you want to view')
    @app_commands.checks.dynamic_cooldown(get_command_cooldown)
    async def monthly(self, interaction: discord.Interaction, username: str=None):
        await interaction.response.defer()
        try: name, uuid = await authenticate_user(username, interaction)
        except TypeError: return
        refined = name.replace("_", "\_")

        discord_id = uuid_to_discord_id(uuid=uuid)
        gmt_offset, hour = get_time_config(discord_id=discord_id)

        with sqlite3.connect('./database/historical.db') as conn:
            cursor = conn.cursor()
            cursor.execute(f"SELECT uuid FROM monthly WHERE uuid = '{uuid}'")
            historical_data = cursor.fetchone()

        if not historical_data:
            start_historical(uuid=uuid)
            await interaction.followup.send(f'Historical stats for {refined} will now be tracked.')
            return

        await interaction.followup.send(self.LOADING_MSG)
        os.makedirs(f'./database/activerenders/{interaction.id}')
        skin_res = fetch_skin_model(uuid, 144)
        hypixel_data = get_hypixel_data(uuid)

        now = datetime.now(timezone(timedelta(hours=gmt_offset)))
        formatted_date = now.strftime(f"%b {now.day}{ordinal(now.day)}, %Y")

        next_occurrence = now.replace(hour=hour, minute=0, second=0, microsecond=0)
        if now >= next_occurrence:
            next_occurrence = next_occurrence.replace(day=1, month=next_occurrence.month + 1)
        while next_occurrence.day != 1:
            next_occurrence += timedelta(days=1)
        utc_next_occurrence = next_occurrence.astimezone(timezone.utc)
        timestamp = int(utc_next_occurrence.timestamp())

        kwargs = {
            "name": name,
            "uuid": uuid,
            "method": "monthly",
            "relative_date": formatted_date,
            "title": "Monthly BW Stats",
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
        update_command_stats(interaction.user.id, 'monthly')


    @app_commands.command(name="lastmonth", description="View last months stats of a player")
    @app_commands.autocomplete(username=username_autocompletion)
    @app_commands.describe(username='The player you want to view', months='The lookback amount in months')
    @app_commands.checks.dynamic_cooldown(get_command_cooldown)
    async def lastmonth(self, interaction: discord.Interaction, username: str=None, months: int=1):
        await interaction.response.defer()
        try: name, uuid = await authenticate_user(username, interaction)
        except TypeError: return

        refined = name.replace("_", "\_")
        discord_id = uuid_to_discord_id(uuid=uuid)

        max_lookback = await get_lookback_eligiblility(interaction=interaction, discord_id=discord_id)
        if -1 != max_lookback < (months * 30):
            await message_invalid_lookback(interaction=interaction, max_lookback=max_lookback)
            return
        if months < 1:
            months = 1

        gmt_offset = get_time_config(discord_id=discord_id)[0]

        now = datetime.now(timezone(timedelta(hours=gmt_offset)))
        relative_date = now - relativedelta(months=months)
        formatted_date = relative_date.strftime("%b %Y")

        try:
            table_name = relative_date.strftime("monthly_%Y_%m")
        except ValueError:
            await interaction.followup.send('Big, big number... too big number...')
            return

        with sqlite3.connect('./database/historical.db') as conn:
            cursor = conn.cursor()
            try:
                cursor.execute(f"SELECT uuid FROM {table_name} WHERE uuid = '{uuid}'")
                historical_data = cursor.fetchone()
            except sqlite3.OperationalError:
                historical_data = ()

        if not historical_data:
            await interaction.followup.send(f'{refined} has no tracked data for {months} month(s) ago!')
            return

        await interaction.followup.send(self.LOADING_MSG)
        os.makedirs(f'./database/activerenders/{interaction.id}')
        skin_res = fetch_skin_model(uuid, 144)
        hypixel_data = get_hypixel_data(uuid)

        kwargs = {
            "name": name,
            "uuid": uuid,
            "method": "lastmonth",
            "relative_date": formatted_date,
            "title": f"{months} Months Ago",
            "table_name": table_name,
            "hypixel_data": hypixel_data,
            "skin_res": skin_res,
            "save_dir": interaction.id
        }
        
        await send_generic_renders(interaction, render_historical, kwargs)
        update_command_stats(interaction.user.id, 'lastmonth')

async def setup(client: commands.Bot) -> None:
    await client.add_cog(Monthly(client))
