import sys
import time
import datetime
from json import load as load_json

import discord
from discord.ext import commands

import statalib as lib
import helper


def calculate_uptime() -> datetime.timedelta:
    with open(f'{lib.REL_PATH}/database/uptime.json') as datafile:
        start_time = load_json(datafile)['start_time']

    time_since_started = int(round(time.time() - start_time))
    return datetime.timedelta(seconds=time_since_started)


class InfoCommandCog(commands.Cog):
    def __init__(self, client: helper.Client):
        self.client: helper.Client = client

    @helper.decorators.app_command("info")
    @helper.interactions.access_permitted_check()
    async def info(self, interaction: discord.Interaction):
        await interaction.response.defer()

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


async def setup(client: helper.Client) -> None:
    await client.add_cog(InfoCommandCog(client))
