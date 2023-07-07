import os
import sys
import time
import datetime
import sqlite3
from json import load as load_json

import psutil
import discord
from discord import app_commands
from discord.ext import commands

from helper.functions import (
    update_command_stats,
    get_command_users,
    get_config,
    load_embeds
)


class Info(commands.Cog):
    def __init__(self, client):
        self.client: discord.Client = client


    @app_commands.command(name="info", description="View information and stats for Statalytics")
    async def info(self, interaction: discord.Interaction):
        await interaction.response.defer()

        # Usage metrics
        with sqlite3.connect('./database/core.db') as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT overall FROM command_usage WHERE discord_id = 0')
            result = cursor.fetchone()
            commands_ran = 0 if not result else result[0]

        with sqlite3.connect('./database/core.db') as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT COUNT(discord_id) FROM linked_accounts')
            result = cursor.fetchone()
            linked_accounts = 0 if not result else result[0]

        # Other shit
        total_guilds = len(self.client.guilds)
        total_users = get_command_users()

        with open('./database/uptime.json') as datafile:
            start_time = load_json(datafile)['start_time']

        uptime = str(datetime.timedelta(seconds=int(round(time.time()-start_time))))
        config = get_config()

        ping = round(self.client.latency * 1000)
        total_commands = len(list(self.client.tree.walk_commands()))

        python_version = '.'.join(str(ver) for ver in sys.version_info[0:3])
        ram_usage = round(psutil.Process(os.getpid()).memory_info().rss / 1024 ** 2, 2)

        format_values = {
            't': '┌', 'c': '├', 'b': '└', 'br': '\u200B', # Special chars
            'uptime': uptime,
            'ping': f'{ping:,}',
            'commands': f'{total_commands:,}',
            'version': config['version'],
            'servers': f'{total_guilds:,}',
            'users': f'{total_users:,}',
            'commands_ran': f'{commands_ran:,}',
            'linked_users': f'{linked_accounts:,}',
            'devs': ', '.join(config["developers"]),
            'library': 'discord.py',
            'python_ver': python_version,
            'ram_usage': ram_usage
        }

        embeds = load_embeds('info', format_values, color='primary')
        await interaction.followup.send(embeds=embeds)

        update_command_stats(discord_id=interaction.user.id, command='info')


async def setup(client: commands.Bot) -> None:
    await client.add_cog(Info(client))
