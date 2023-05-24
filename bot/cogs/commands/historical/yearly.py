import os
import json
import time
import sqlite3
import traceback
import asyncio

from datetime import datetime, timedelta, timezone

import discord
from discord import app_commands
from discord.ext import commands, tasks

from render.historical import render_historical
from ui import SelectView
from functions import (username_autocompletion,
                       check_subscription,
                       get_hypixel_data,
                       update_command_stats,
                       authenticate_user,
                       start_historical,
                       get_subscription,
                       save_historical,
                       uuid_to_discord_id,
                       get_time_config,
                       skin_session)


async def is_eligible(interaction: discord.Interaction, discord_id: int) -> bool:
    subscription = None
    if discord_id:
        subscription = get_subscription(discord_id=discord_id)
    if not subscription and not get_subscription(interaction.user.id):
        with open('./config.json', 'r') as datafile:
            config = json.load(datafile)
        embed_color = int(config['embed_primary_color'], base=16)
        embed = discord.Embed(title="That player doesn't have premium!", description='In order to view yearly stats, a [premium subscription](https://statalytics.net/store) is required!', color=embed_color)
        embed.add_field(name='How does it work?', value="""
            \- You can view any player's yearly stats if you have a premium subscription.
            \- You can view a player's yearly stats if they have a premium subscription.\n
            Yearly stats can be tracked but not viewed without a premium subscription
        """.replace('   ', ''))
        await interaction.response.send_message(embed=embed)
        return False
    return True

class Yearly(commands.Cog):
    def __init__(self, client):
        self.client = client
        self.GENERATING_MESSAGE = 'Generating please wait <a:loading1:1062561739989860462>'

    @tasks.loop(hours=1)
    async def reset_yearly(self):
        utc_now = datetime.utcnow()
        if not utc_now.timetuple().tm_yday in (1, 2, 365, 366):
            return

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

            cursor.execute('SELECT * FROM yearly')
            yearly_data = cursor.fetchall()

        for yearly in yearly_data:
            start_time = time.time()
            linked_account = linked_data.get(yearly[0])
            if linked_account:
                time_preference = config_data.get(linked_account, (0, 0, 0))
                gmt_offset, hour = time_preference[1], time_preference[2]
            else: gmt_offset, hour = 0, 0

            timezone = utc_now + timedelta(hours=gmt_offset)
            if timezone.timetuple().tm_yday == 1 and timezone.hour == hour:
                hypixel_data = get_hypixel_data(yearly[0], cache=False)

                with open('./config.json', 'r') as datafile:
                    stat_keys: list = json.load(datafile)['tracked_bedwars_stats']
                stat_values = [hypixel_data["player"].get("achievements", {}).get("bedwars_level", 0)]

                for key in stat_keys:
                    stat_values.append(hypixel_data["player"].get("stats", {}).get("Bedwars", {}).get(key, 0))
                stat_keys.insert(0, 'level')

                with sqlite3.connect('./database/historical.db') as conn:
                    cursor = conn.cursor()

                    set_clause = ', '.join([f"{column} = ?" for column in stat_keys])
                    cursor.execute(f"UPDATE yearly SET {set_clause} WHERE uuid = '{yearly[0]}'", stat_values)

                stat_values.insert(0, yearly[0])
                table_name = (timezone - timedelta(days=1)).strftime("yearly_%Y")
                save_historical(yearly, stat_values, table=table_name)

                sleep_time = 0.5 - (time.time() - start_time)
                await asyncio.sleep(sleep_time)

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


    @app_commands.command(name = "yearly", description = "View the yearly stats of a player")
    @app_commands.autocomplete(username=username_autocompletion)
    @app_commands.describe(username='The player you want to view')
    @app_commands.checks.dynamic_cooldown(check_subscription)
    async def yearly(self, interaction: discord.Interaction, username: str=None):
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
            await interaction.response.defer()
            start_historical(uuid=uuid, method='yearly')
            await interaction.followup.send(f'Yearly stats for {refined} will now be tracked.')
            return

        result = await is_eligible(interaction, discord_id)
        if not result: return

        await interaction.response.send_message(self.GENERATING_MESSAGE)
        os.makedirs(f'./database/activerenders/{interaction.id}')
        skin_res = skin_session.get(f'https://visage.surgeplay.com/bust/144/{uuid}', timeout=10)
        hypixel_data = get_hypixel_data(uuid)

        now = datetime.now(timezone(timedelta(hours=gmt_offset)))
        if hour > 0: hour -= 1
        next_occurrence = datetime(now.year + 1, 1, 1, hour, 0, 0, tzinfo=timezone(timedelta(hours=gmt_offset)))
        utc_next_occurrence = next_occurrence.astimezone(timezone.utc)
        timestamp = int(utc_next_occurrence.timestamp())

        render_historical(name, uuid, method="yearly", mode="Overall", hypixel_data=hypixel_data, skin_res=skin_res.content, save_dir=interaction.id)
        view = SelectView(user=interaction.user.id, inter=interaction, mode='Select a mode')
        await interaction.edit_original_response(content=f':alarm_clock: Resets <t:{timestamp}:R>', attachments=[discord.File(f"./database/activerenders/{interaction.id}/overall.png")], view=view)
        render_historical(name, uuid, method="yearly", mode="Solos", hypixel_data=hypixel_data, skin_res=skin_res.content, save_dir=interaction.id)
        render_historical(name, uuid, method="yearly", mode="Doubles", hypixel_data=hypixel_data, skin_res=skin_res.content, save_dir=interaction.id)
        render_historical(name, uuid, method="yearly", mode="Threes", hypixel_data=hypixel_data, skin_res=skin_res.content, save_dir=interaction.id)
        render_historical(name, uuid, method="yearly", mode="Fours", hypixel_data=hypixel_data, skin_res=skin_res.content, save_dir=interaction.id)
        render_historical(name, uuid, method="yearly", mode="4v4", hypixel_data=hypixel_data, skin_res=skin_res.content, save_dir=interaction.id)

        update_command_stats(interaction.user.id, 'yearly')

    @app_commands.command(name = "lastyear", description = "View last years stats of a player")
    @app_commands.autocomplete(username=username_autocompletion)
    @app_commands.describe(username='The player you want to view')
    @app_commands.checks.dynamic_cooldown(check_subscription)
    async def lastyear(self, interaction: discord.Interaction, username: str=None):
        try: name, uuid = await authenticate_user(username, interaction)
        except TypeError: return
        refined = name.replace("_", "\_")

        discord_id = uuid_to_discord_id(uuid)
        result = await is_eligible(interaction, discord_id)
        if not result: return

        gmt_offset = get_time_config(discord_id=discord_id)[0]

        now = datetime.now(timezone(timedelta(hours=gmt_offset)))
        table_name = (now - timedelta(days=365)).strftime("yearly_%Y")

        with sqlite3.connect('./database/historical.db') as conn:
            cursor = conn.cursor()
            try:
                cursor.execute(f"SELECT uuid FROM {table_name} WHERE uuid = '{uuid}'")
                historical_data = cursor.fetchone()
            except sqlite3.OperationalError:
                historical_data = ()

        if not historical_data:
            await interaction.response.send_message(f'{refined} has no tracked data for last year!')
            return

        await interaction.response.send_message(self.GENERATING_MESSAGE)
        os.makedirs(f'./database/activerenders/{interaction.id}')
        skin_res = skin_session.get(f'https://visage.surgeplay.com/bust/144/{uuid}', timeout=10)
        hypixel_data = get_hypixel_data(uuid)
    
        render_historical(name, uuid, method="lastyear", table_name=table_name, mode="Overall", hypixel_data=hypixel_data, skin_res=skin_res.content, save_dir=interaction.id)
        view = SelectView(user=interaction.user.id, inter=interaction, mode='Select a mode')
        await interaction.edit_original_response(content=None, attachments=[discord.File(f"./database/activerenders/{interaction.id}/overall.png")], view=view)
        render_historical(name, uuid, method="lastyear", table_name=table_name, mode="Solos", hypixel_data=hypixel_data, skin_res=skin_res.content, save_dir=interaction.id)
        render_historical(name, uuid, method="lastyear", table_name=table_name, mode="Doubles", hypixel_data=hypixel_data, skin_res=skin_res.content, save_dir=interaction.id)
        render_historical(name, uuid, method="lastyear", table_name=table_name, mode="Threes", hypixel_data=hypixel_data, skin_res=skin_res.content, save_dir=interaction.id)
        render_historical(name, uuid, method="lastyear", table_name=table_name, mode="Fours", hypixel_data=hypixel_data, skin_res=skin_res.content, save_dir=interaction.id)
        render_historical(name, uuid, method="lastyear", table_name=table_name, mode="4v4", hypixel_data=hypixel_data, skin_res=skin_res.content, save_dir=interaction.id)

        update_command_stats(interaction.user.id, 'lastyear')


async def setup(client: commands.Bot) -> None:
    await client.add_cog(Yearly(client))
