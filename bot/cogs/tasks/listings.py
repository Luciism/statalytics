from os import getenv

import requests
import discord
from discord.ext import commands, tasks

from statalib import (
    get_user_total,
    to_thread,
    align_to_hour,
    log_error_msg
)


class Listings(commands.Cog):
    def __init__(self, client):
        self.client: commands.Bot = client

        self.TOPGG_TOKEN = getenv('TOPGG_TOKEN')
        self.DBL_TOKEN = getenv('DBL_TOKEN')
        self.DISCORDS_TOKEN = getenv('DISCORDS_TOKEN')
        self.BOTLIST_TOKEN = getenv('BOTLIST_TOKEN')


    @to_thread
    def update_listings(self):
        guild_count = len(self.client.guilds)
        total_users = get_user_total()

        client_id = self.client.user.id

        requests.post(
            url=f'https://top.gg/api/bots/{client_id}/stats',
            data={'server_count': guild_count},
            headers={'Authorization': self.TOPGG_TOKEN},
            timeout=10
        )

        requests.post(
            url=f'https://discordbotlist.com/api/v1/bots/{client_id}/stats',
            data={
                'guilds': guild_count,
                'users': total_users
            },
            headers={'Authorization': self.DBL_TOKEN},
            timeout=10
        )

        requests.post(
            url=f'https://discords.com/bots/api/bot/{client_id}',
            data={'server_count': guild_count},
            headers={'Authorization': self.DISCORDS_TOKEN},
            timeout=10
        )

        requests.post(
            url=f'https://api.botlist.me/api/v1/bots/{client_id}/stats',
            data={'server_count': guild_count},
            headers={'Authorization': self.BOTLIST_TOKEN},
            timeout=10
        )


    @tasks.loop(hours=1)
    async def update_listings_loop(self):
        await self.update_listings()


    @update_listings_loop.error
    async def on_update_listings_error(self, error):
        await log_error_msg(self.client, error)


    async def cog_load(self):
        if getenv('ENVIRONMENT') == 'production':
            self.update_listings_loop.start()


    async def cog_unload(self):
        self.update_listings_loop.cancel()


    @update_listings_loop.before_loop
    async def before_update_listings(self):
        await align_to_hour()


async def setup(client: commands.Bot) -> None:
    await client.add_cog(Listings(client))
