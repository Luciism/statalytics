import asyncio
import os
import logging
from datetime import datetime
from typing_extensions import override

from aiohttp import ClientError, ClientSession, ClientTimeout
from discord.ext import commands, tasks

import statalib as lib
import helper

logger = logging.getLogger(__name__)


class BotListingUpdatesCog(commands.Cog):
    def __init__(self, client: helper.Client):
        self.client: helper.Client = client

        self.TOPGG_TOKEN: str = os.getenv('TOPGG_TOKEN') or ""
        self.DBL_TOKEN: str = os.getenv('DBL_TOKEN') or ""
        self.DISCORDS_TOKEN: str = os.getenv('DISCORDS_TOKEN') or ""
        self.BOTLIST_TOKEN: str = os.getenv('BOTLIST_TOKEN') or ""


    @tasks.loop(hours=1)
    async def update_listings_loop(self):
        await self.client.wait_until_ready()

        guild_count = len(self.client.guilds)
        total_users = lib.usage.get_user_total()

        client_id = self.client.user.id

        async with ClientSession() as session:
            res1 = await session.post(
                url=f'https://top.gg/api/bots/{client_id}/stats',
                data={'server_count': guild_count},
                headers={'Authorization': self.TOPGG_TOKEN},
                timeout=ClientTimeout(total=10)
            )

            res2 = await session.post(
                url=f'https://discordbotlist.com/api/v1/bots/{client_id}/stats',
                data={
                    'guilds': guild_count,
                    'users': total_users
                },
                headers={'Authorization': self.DBL_TOKEN},
                timeout=ClientTimeout(total=10)
            )

            res3 = await session.post(
                url=f'https://discords.com/bots/api/bot/{client_id}',
                data={'server_count': guild_count},
                headers={'Authorization': self.DISCORDS_TOKEN},
                timeout=ClientTimeout(total=10)
            )

            res4 = await session.post(
                url=f'https://api.botlist.me/api/v1/bots/{client_id}/stats',
                data={'server_count': guild_count},
                headers={'Authorization': self.BOTLIST_TOKEN},
                timeout=ClientTimeout(total=10)
            )

        try:
            res1.raise_for_status()
            res2.raise_for_status()
            res3.raise_for_status()
            res4.raise_for_status()
        except ClientError as exc:
            logger.error("Bot listing update failed:", exc_info=exc)


    @update_listings_loop.error
    async def on_update_listings_error(self, error: BaseException):
        if not isinstance(error, Exception):
            return

        await lib.handlers.log_error_msg(self.client, error)
        self.update_listings_loop.restart()


    @override
    async def cog_load(self):
        if os.getenv('ENVIRONMENT') == 'production':
            _ = self.update_listings_loop.start()


    @override
    async def cog_unload(self):
        self.update_listings_loop.cancel()


    @update_listings_loop.before_loop
    async def before_update_listings(self):
        now = datetime.now()
        sleep_seconds = (60 - now.minute) * 60 - now.second
        await asyncio.sleep(sleep_seconds)



async def setup(client: helper.Client) -> None:
    await client.add_cog(BotListingUpdatesCog(client))
