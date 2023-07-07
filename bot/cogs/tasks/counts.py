import os
import asyncio
from datetime import datetime

import requests
import discord
from discord.ext import commands, tasks

from helper.functions import get_command_users, to_thread


class Counts(commands.Cog):
    def __init__(self, client):
        self.client: discord.Client = client
        self.TOPGG_TOKEN = os.getenv('STATALYTICS_TOPGG_TOKEN')
        self.DBL_TOKEN = os.getenv('STATALYTICS_DBL_TOKEN')
        self.DISCORDS_TOKEN = os.getenv('STATALYTICS_DISCORDS_TOKEN')
        self.BOTLIST_TOKEN = os.getenv('STATALYTICS_BOTLIST_TOKEN')


    @to_thread
    def update_counts(self):
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


    @tasks.loop(hours=1)
    async def update_counts_loop(self):
        await self.update_counts()


    async def cog_load(self):
        if os.getenv('STATALYTICS_ENVIRONMENT') == 'production':
            self.update_counts_loop.start()


    async def cog_unload(self):
        self.update_counts_loop.cancel()


    @update_counts_loop.before_loop
    async def before_update_counts(self):
        now = datetime.now()
        sleep_seconds = (60 - now.minute) * 60 - now.second
        await asyncio.sleep(sleep_seconds)


async def setup(client: commands.Bot) -> None:
    await client.add_cog(Counts(client))
