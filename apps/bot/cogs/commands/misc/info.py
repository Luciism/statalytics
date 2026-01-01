import sys
import time
import datetime
from json import load as load_json

import discord
from discord import app_commands
from discord.ext import commands

import statalib as lib
import helper


def calculate_uptime() -> datetime.timedelta:
    with open(f'{lib.REL_PATH}/database/uptime.json') as datafile:
        start_time = load_json(datafile)['start_time']

    time_since_started = int(round(time.time() - start_time))
    return datetime.timedelta(seconds=time_since_started)


class Info(commands.Cog):
    def __init__(self, client):
        self.client: commands.Bot = client


    @app_commands.command(
        name="info",
        description="View information and stats for Statalytics")
    @app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
    @app_commands.allowed_installs(guilds=True, users=True)
    async def info(self, interaction: discord.Interaction):
        await interaction.response.defer()
        await helper.interactions.run_interaction_checks(interaction)

        # process_mem = psutil.Process(os.getpid()).memory_info().rss
        # ram_usage = round(process_mem / 1024 ** 2, 2)

        embed = helper.Embeds.misc.services_info({
            'uptime': str(calculate_uptime()),
            'ping': f'{round(self.client.latency * 1000):,}',
            'commands': f'{len(list(self.client.tree.walk_commands())):,}',

            'servers': f'{len(self.client.guilds):,}',
            'users': f'{lib.usage.get_user_total():,}',
            'commands_ran': f'{lib.usage.get_commands_total():,}',
            'linked_users': f'{lib.accounts.get_total_linked_accounts():,}',

            'python_ver': '.'.join(str(ver) for ver in sys.version_info[0:3]),
            'shard_count': self.client.shard_count
        })
        await interaction.followup.send(embed=embed)

        lib.usage.update_command_stats(discord_id=interaction.user.id, command='info')


async def setup(client: commands.Bot) -> None:
    await client.add_cog(Info(client))
