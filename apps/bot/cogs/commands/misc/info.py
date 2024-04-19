import os
import sys
import time
import datetime
from json import load as load_json

import discord
from discord import app_commands
from discord.ext import commands

import statalib as lib


class Info(commands.Cog):
    def __init__(self, client):
        self.client: commands.Bot = client


    @app_commands.command(
        name="info",
        description="View information and stats for Statalytics")
    async def info(self, interaction: discord.Interaction):
        await interaction.response.defer()
        await lib.run_interaction_checks(interaction)

        commands_ran = lib.get_commands_total()
        linked_accounts = lib.get_linked_total()

        total_guilds = len(self.client.guilds)
        total_users = lib.get_user_total()

        with open(f'{lib.REL_PATH}/database/uptime.json') as datafile:
            start_time = load_json(datafile)['start_time']

        time_since_started = int(round(time.time() - start_time))
        uptime = str(datetime.timedelta(seconds=time_since_started))

        config: dict = lib.config()

        ping = round(self.client.latency * 1000)
        total_commands = len(list(self.client.tree.walk_commands()))

        python_version = '.'.join(str(ver) for ver in sys.version_info[0:3])

        shard_count = self.client.shard_count
        # process_mem = psutil.Process(os.getpid()).memory_info().rss
        # ram_usage = round(process_mem / 1024 ** 2, 2)

        format_values = {
            'fields': {
                0: {
                    'value': {
                        'uptime': uptime,
                        'ping': f'{ping:,}',
                        'commands': f'{total_commands:,}',
                        'version': config.get('apps.bot.version'),
                    }
                },
                2: {
                    'value': {
                    'servers': f'{total_guilds:,}',
                    'users': f'{total_users:,}',
                    'commands_ran': f'{commands_ran:,}',
                    'linked_users': f'{linked_accounts:,}'
                    }
                },
                3: {
                    'value': {
                        'devs': ', '.join(lib.config("global.developers")),
                        'library': 'discord.py',
                        'python_ver': python_version,
                        'shard_count': shard_count
                    }
                }
            }
        }

        embeds = lib.load_embeds('info', format_values, color='primary')
        await interaction.followup.send(embeds=embeds)

        lib.update_command_stats(discord_id=interaction.user.id, command='info')


async def setup(client: commands.Bot) -> None:
    await client.add_cog(Info(client))
