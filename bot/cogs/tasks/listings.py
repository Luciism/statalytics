from os import getenv

from aiohttp import ClientSession
from discord.ext import commands, tasks

import statalib as lib


class Listings(commands.Cog):
    def __init__(self, client):
        self.client: commands.Bot = client

        self.TOPGG_TOKEN = getenv('TOPGG_TOKEN')
        self.DBL_TOKEN = getenv('DBL_TOKEN')
        self.DISCORDS_TOKEN = getenv('DISCORDS_TOKEN')
        self.BOTLIST_TOKEN = getenv('BOTLIST_TOKEN')


    @tasks.loop(hours=1)
    async def update_listings_loop(self):
        await self.client.wait_until_ready()

        guild_count = len(self.client.guilds)
        total_users = lib.get_user_total()

        client_id = self.client.user.id

        async with ClientSession() as session:
            await session.post(
                url=f'https://top.gg/api/bots/{client_id}/stats',
                data={'server_count': guild_count},
                headers={'Authorization': self.TOPGG_TOKEN},
                timeout=10
            )

            await session.post(
                url=f'https://discordbotlist.com/api/v1/bots/{client_id}/stats',
                data={
                    'guilds': guild_count,
                    'users': total_users
                },
                headers={'Authorization': self.DBL_TOKEN},
                timeout=10
            )

            await session.post(
                url=f'https://discords.com/bots/api/bot/{client_id}',
                data={'server_count': guild_count},
                headers={'Authorization': self.DISCORDS_TOKEN},
                timeout=10
            )

            await session.post(
                url=f'https://api.botlist.me/api/v1/bots/{client_id}/stats',
                data={'server_count': guild_count},
                headers={'Authorization': self.BOTLIST_TOKEN},
                timeout=10
            )


    @update_listings_loop.error
    async def on_update_listings_error(self, error):
        await lib.log_error_msg(self.client, error)


    async def cog_load(self):
        if getenv('ENVIRONMENT') == 'production':
            self.update_listings_loop.start()


    async def cog_unload(self):
        self.update_listings_loop.cancel()


    @update_listings_loop.before_loop
    async def before_update_listings(self):
        await lib.align_to_hour()


async def setup(client: commands.Bot) -> None:
    await client.add_cog(Listings(client))
