import os
import json
import psutil
import sys
import time
import datetime
import sqlite3
from json import load as load_json

import discord
from discord import app_commands
from discord.ext import commands

from helper.functions import (
    update_command_stats,
    get_command_users,
    get_embed_color,
    get_config
)


class Info(commands.Cog):
    def __init__(self, client):
        self.client: discord.Client = client


    @app_commands.command(name="info", description="View information and stats for Statalytics")
    async def info(self, interaction: discord.Interaction):
        await interaction.response.defer()

        # Usage metrics
        with sqlite3.connect('./database/command_usage.db') as conn:
            cursor = conn.cursor()
            cursor.execute(
                f'SELECT commands_ran FROM overall WHERE discord_id = 0')
            total_commands_ran = cursor.fetchone()[0]

        with sqlite3.connect('./database/linked_accounts.db') as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT COUNT(discord_id) FROM linked_accounts')
            total_linked_accounts = cursor.fetchone()[0]

        # Other shit
        total_guilds = len(self.client.guilds)
        total_users = get_command_users()

        with open('./database/uptime.json') as datafile:
            start_time = load_json(datafile)['start_time']

        uptime = str(datetime.timedelta(seconds=int(round(time.time()-start_time))))
        config = get_config()

        ping = round(self.client.latency * 1000)
        total_commands = len(list(self.client.tree.walk_commands()))

        python_version = '.'.join((str(sys.version_info[0]), str(sys.version_info[1]), str(sys.version_info[2])))
        ram_usage = round(psutil.Process(os.getpid()).memory_info().rss / 1024 ** 2, 2)

        with open('./assets/embeds/info.json', 'r') as datafile:
            info_embed_str: str = json.load(datafile)['embeds'][0]

        info_embed_str = info_embed_str.format(
            t='┌', c='├', b='└', br='​', # Special chars
            embed_color=get_embed_color('primary'),
            uptime=uptime,
            ping=f'{ping:,}',
            commands=f'{total_commands:,}',
            version=config['version'],
            servers=f'{total_guilds:,}',
            users=f'{total_users:,}',
            commands_ran=f'{total_commands_ran:,}',
            linked_users=f'{total_linked_accounts:,}',
            devs=', '.join(config["developers"]),
            library='discord.py',
            python_ver=python_version,
            ram_usage=ram_usage
        ).replace("{{", "{").replace("}}", "}")

        embed = discord.Embed.from_dict(json.loads(info_embed_str))

        await interaction.followup.send(embed=embed)

        update_command_stats(discord_id=interaction.user.id, command='info')


async def setup(client: commands.Bot) -> None:
    await client.add_cog(Info(client))
