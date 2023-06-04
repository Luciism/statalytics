import os
import time
import json
import sqlite3
import asyncio
import traceback
from datetime import datetime, timedelta, timezone

import discord
from discord import app_commands
from discord.ext import commands, tasks

from render.historical import render_historical
from helper.functions import (username_autocompletion,
                       get_command_cooldown,
                       get_hypixel_data,
                       update_command_stats,
                       authenticate_user,
                       start_historical,
                       save_historical,
                       uuid_to_discord_id,
                       get_time_config,
                       get_lookback_eligiblility,
                       message_invalid_lookback,
                       fetch_skin_model,
                       ordinal,
                       send_generic_renders)


class Daily(commands.Cog):
    def __init__(self, client):
        self.client: discord.Client = client
        self.GENERATING_MESSAGE = 'Generating please wait <a:loading1:1062561739989860462>'


    @tasks.loop(hours=1)
    async def reset_daily(self):
        with sqlite3.connect('./database/linked_accounts.db') as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM linked_accounts')
            row = cursor.fetchone()

            linked_data = {}
            while row:
                linked_data[row[1]] = row[0]
                row = cursor.fetchone()

        with sqlite3.connect('./database/historical.db') as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM configuration')
            row = cursor.fetchone()

            config_data = {}
            while row:
                config_data[row[0]] = row
                row = cursor.fetchone()

            cursor.execute('SELECT * FROM daily')
            daily_data = cursor.fetchall()

        utc_now = datetime.utcnow()
        for daily in daily_data:
            start_time = time.time()
            linked_account = linked_data.get(daily[0])
            if linked_account:
                time_preference = config_data.get(linked_account, (0, 0, 0))
                gmt_offset, hour = time_preference[1], time_preference[2]
            else: gmt_offset, hour = 0, 0

            timezone = utc_now + timedelta(hours=gmt_offset)
            target_hour = timezone.hour
            if target_hour == hour:
                hypixel_data = get_hypixel_data(daily[0], cache=False)

                with open('./config.json', 'r') as datafile:
                    stat_keys: list = json.load(datafile)['tracked_bedwars_stats']
                stat_values = [hypixel_data["player"].get("achievements", {}).get("bedwars_level", 0)]

                for key in stat_keys:
                    stat_values.append(hypixel_data["player"].get("stats", {}).get("Bedwars", {}).get(key, 0))
                stat_keys.insert(0, 'level')

                with sqlite3.connect('./database/historical.db') as conn:
                    cursor = conn.cursor()

                    set_clause = ', '.join([f"{column} = ?" for column in stat_keys])
                    cursor.execute(f"UPDATE daily SET {set_clause} WHERE uuid = '{daily[0]}'", stat_values)

                stat_values.insert(0, daily[0])
                table_name = (timezone - timedelta(days=1)).strftime("daily_%Y_%m_%d")
                save_historical(daily, stat_values, table=table_name)

                sleep_time = 1 - (time.time() - start_time)
                await asyncio.sleep(sleep_time)


    def cog_load(self):
        self.reset_daily.start()


    def cog_unload(self):
        self.reset_daily.cancel()


    @reset_daily.error
    async def on_reset_daily_error(self, error):
        traceback_str = ''.join(traceback.format_exception(type(error), error, error.__traceback__))
        print(traceback_str)

        with open('./config.json', 'r') as datafile: config = json.load(datafile)
        await self.client.wait_until_ready()
        channel = self.client.get_channel(config.get('error_logs_channel_id'))

        if len(traceback_str) > 1988:
            for i in range(0, len(traceback_str), 1988):
                substring = traceback_str[i:i+1988]
                await channel.send(f'```cmd\n{substring}\n```')
        else:
            await channel.send(f'```cmd\n{traceback_str[-1988:]}\n```')

    @reset_daily.before_loop
    async def before_reset_daily(self):
        now = datetime.now()
        sleep_seconds = (60 - now.minute) * 60 - now.second
        await asyncio.sleep(sleep_seconds)


    @app_commands.command(name = "daily", description = "View the daily stats of a player")
    @app_commands.autocomplete(username=username_autocompletion)
    @app_commands.describe(username='The player you want to view')
    @app_commands.checks.dynamic_cooldown(get_command_cooldown)
    async def daily(self, interaction: discord.Interaction, username: str=None):
        try: name, uuid = await authenticate_user(username, interaction)
        except TypeError: return
        refined = name.replace("_", "\_")

        discord_id = uuid_to_discord_id(uuid=uuid)
        gmt_offset, hour = get_time_config(discord_id=discord_id)

        with sqlite3.connect('./database/historical.db') as conn:
            cursor = conn.cursor()
            cursor.execute(f"SELECT uuid FROM daily WHERE uuid = '{uuid}'")
            historical_data = cursor.fetchone()

        if not historical_data:
            await interaction.response.defer()
            start_historical(uuid=uuid, method='daily')
            await interaction.followup.send(f'Daily stats for {refined} will now be tracked.')
            return

        await interaction.response.send_message(self.GENERATING_MESSAGE)
        os.makedirs(f'./database/activerenders/{interaction.id}')
        skin_res = fetch_skin_model(uuid, 144)
        hypixel_data = get_hypixel_data(uuid)

        now = datetime.now(timezone(timedelta(hours=gmt_offset)))
        formatted_date = now.strftime(f"%b {now.day}{ordinal(now.day)}, %Y")

        next_occurrence = now.replace(hour=hour, minute=0, second=0, microsecond=0)
        if now >= next_occurrence: next_occurrence += timedelta(days=1)
        utc_next_occurrence = next_occurrence.astimezone(timezone.utc)
        timestamp = int(utc_next_occurrence.timestamp())

        kwargs = {
            "name": name,
            "uuid": uuid,
            "method": "daily",
            "relative_date": formatted_date,
            "title": "Daily BW Stats",
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
        update_command_stats(interaction.user.id, 'daily')


    @app_commands.command(name = "lastday", description = "View yesterdays stats of a player")
    @app_commands.autocomplete(username=username_autocompletion)
    @app_commands.describe(username='The player you want to view', days='The lookback amount in days')
    @app_commands.checks.dynamic_cooldown(get_command_cooldown)
    async def lastday(self, interaction: discord.Interaction, username: str=None, days: int=1):
        try: name, uuid = await authenticate_user(username, interaction)
        except TypeError: return
        refined = name.replace("_", "\_")

        discord_id = uuid_to_discord_id(uuid=uuid)
        max_lookback = await get_lookback_eligiblility(interaction=interaction, discord_id=discord_id)
        if -1 != max_lookback < days:
            await message_invalid_lookback(interaction=interaction, max_lookback=max_lookback)
            return
        if days < 1: days = 1

        gmt_offset = get_time_config(discord_id=discord_id)[0]

        now = datetime.now(timezone(timedelta(hours=gmt_offset)))
        relative_date = now - timedelta(days=days)
        formatted_date = relative_date.strftime(f"%b {relative_date.day}{ordinal(relative_date.day)}, %Y")

        try:
            table_name = relative_date.strftime("daily_%Y_%m_%d")
        except OverflowError:
            await interaction.response.send_message('Big, big number... too big number...')
            return

        with sqlite3.connect('./database/historical.db') as conn:
            cursor = conn.cursor()
            try:
                cursor.execute(f"SELECT uuid FROM {table_name} WHERE uuid = '{uuid}'")
                historical_data = cursor.fetchone()
            except sqlite3.OperationalError:
                historical_data = ()

        if not historical_data:
            await interaction.response.send_message(f'{refined} has no tracked data for {days} day(s) ago!')
            return

        await interaction.response.send_message(self.GENERATING_MESSAGE)
        os.makedirs(f'./database/activerenders/{interaction.id}')
        skin_res = fetch_skin_model(uuid, 144)
        hypixel_data = get_hypixel_data(uuid)

        kwargs = {
            "name": name,
            "uuid": uuid,
            "method": "lastday",
            "relative_date": formatted_date,
            "title": f"{days} Days Ago",
            "table_name": table_name,
            "hypixel_data": hypixel_data,
            "skin_res": skin_res,
            "save_dir": interaction.id
        }

        await send_generic_renders(interaction, render_historical, kwargs)
        update_command_stats(interaction.user.id, 'lastday')


async def setup(client: commands.Bot) -> None:
    await client.add_cog(Daily(client))
