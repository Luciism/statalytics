import os
import psutil
import sys
import time
import datetime
import sqlite3
from json import load as load_json

import discord
from discord import app_commands
from discord.ext import commands


class Info(commands.Cog):
    def __init__(self, client):
        self.client = client

    @app_commands.command(name="info", description="View information and stats for Statalytics")
    async def info(self, interaction: discord.Interaction):
        await interaction.response.defer()

        with sqlite3.connect('./database/command_usage.db') as conn:
            cursor = conn.cursor()
            cursor.execute(
                f'SELECT commands_ran FROM overall WHERE discord_id = 0')
            total_commands_ran = cursor.fetchone()[0]

        with sqlite3.connect('./database/linked_accounts.db') as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT COUNT(discord_id) FROM linked_accounts')
            total_linked_accounts = cursor.fetchone()[0]

        total_guilds = len(self.client.guilds)
        total_members = len(self.client.users)

        with open('./uptime.json') as datafile:
            start_time = load_json(datafile)['start_time']

        uptime = str(datetime.timedelta(seconds=int(round(time.time()-start_time))))

        with open('./config.json', 'r') as datafile:
            config = load_json(datafile)

        ping = round(self.client.latency * 1000)
        total_commands = len(list(self.client.tree.walk_commands()))

        embed = discord.Embed(title='Statalytics Info', description=None, color=int(config['embed_primary_color'], base=16))

        embed.add_field(name='Key Metrics', value=f"""
            `┌` **Uptime:** `{uptime}`
            `├` **Ping:** `{ping:,}ms`
            `├` **Commands:** `{total_commands:,}`
            `└` **Version:** `{config['version']}`
        """)

        embed.add_field(name='', value='')

        embed.add_field(name='Bot Usage Stats', value=f"""
            `┌` **Servers:** `{total_guilds:,}`
            `├` **Users:** `{total_members:,}`
            `├` **Commands Ran:** `{total_commands_ran:,}`
            `└` **Linked Users**: `{total_linked_accounts:,}`
        """)

        python_version = '.'.join((str(sys.version_info[0]), str(sys.version_info[1]), str(sys.version_info[2])))
        ram_usage = round(psutil.Process(os.getpid()).memory_info().rss / 1024 ** 2, 2)
        embed.add_field(name='Specifications', value=f"""
            `┌` **Devs:** `{', '.join(config['developers'])}`
            `├` **Library:** `discord.py`
            `├` **Python:** `{python_version}`
            `└` **Used RAM:** `{ram_usage:,}mb`
        """)

        embed.add_field(name='', value='')

        embed.add_field(name='Links', value=f"""
            `┌` [Invite]({config['links']['invite_url']})
            `├` [Website]({config['links']['website']})
            `├` [Support]({config['links']['support_server']})
            `└` [Github]({config['links']['github']})
        """)

        embed.set_thumbnail(url='https://statalytics.net/image/logo.png')

        await interaction.followup.send(embed=embed)


async def setup(client: commands.Bot) -> None:
    await client.add_cog(Info(client))
