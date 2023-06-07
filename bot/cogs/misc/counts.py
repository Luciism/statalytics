import os
import requests
import asyncio
from datetime import datetime

import discord
from discord.ext import commands, tasks

from helper.functions import get_command_users


class Counts(commands.Cog):
    def __init__(self, client):
        self.client: discord.Client = client
        self.TOPGG_TOKEN = os.environ.get('STATALYTICS_TOPGG_TOKEN')
        self.DBL_TOKEN = os.environ.get('STATALYTICS_DBL_TOKEN')
        self.DISCORDS_TOKEN = os.environ.get('STATALYTICS_DISCORDS_TOKEN')
        self.BOTLIST_TOKEN = os.environ.get('STATALYTICS_BOTLIST_TOKEN')


    @tasks.loop(hours=1)
    async def update_counts(self):
        guild_count = len(self.client.guilds)
        total_users = get_command_users()

        requests.post(
            url='https://top.gg/api/bots/903765373181112360/stats',
            data={'server_count': guild_count},
            headers={'Authorization': self.TOPGG_TOKEN},
            timeout=10
        )

        requests.post(
            url='https://discordbotlist.com/api/v1/bots/903765373181112360/stats',
            data={
                'guilds': guild_count,
                'users': total_users
            },
            headers={'Authorization': self.DBL_TOKEN},
            timeout=10
        )

        requests.post(
            url='https://discords.com/bots/api/bot/903765373181112360',
            data={'server_count': guild_count},
            headers={'Authorization': self.DISCORDS_TOKEN},
            timeout=10
        )

        requests.post(
            url='https://api.botlist.me/api/v1/bots/903765373181112360/stats',
            data={'server_count': guild_count},
            headers={'Authorization': self.BOTLIST_TOKEN},
            timeout=10
        )


    def cog_load(self):
        if os.environ.get('STATALYTICS_ENVIRONMENT') == 'production':
            self.update_counts.start()


    def cog_unload(self):
        self.update_counts.cancel()


    @update_counts.before_loop
    async def before_update_counts(self):
        now = datetime.now()
        sleep_seconds = (60 - now.minute) * 60 - now.second
        await asyncio.sleep(sleep_seconds)


async def setup(client: commands.Bot) -> None:
    await client.add_cog(Counts(client))
