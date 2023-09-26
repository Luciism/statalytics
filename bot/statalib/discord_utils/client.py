import json
import logging
from datetime import datetime

import discord
from discord.ext import commands

from ..functions import get_config
from ..views import add_info_view

logger = logging.getLogger('statalytics')


class Client(commands.Bot):
    def __init__(self, *, intents: discord.Intents=None):
        if intents is None:
            intents = discord.Intents(messages=True)
            intents.guilds = True

        super().__init__(
            intents=intents,
            command_prefix=commands.when_mentioned_or('$')
        )

    async def setup_hook(self):
        cogs = get_config('enabled_cogs')
        for ext in cogs:
            try:
                await self.load_extension(f'cogs.{ext}')
                logger.info(f"Loaded cog: {ext}")
            except commands.errors.ExtensionNotFound:
                logger.info(f"Cog doesn't exist: {ext}")

        add_info_view(self)

        # await self.tree.sync()
        with open('./database/uptime.json', 'w') as datafile:
            json.dump({"start_time": datetime.utcnow().timestamp()}, datafile, indent=4)


    async def on_ready(self):
        logger.info(f'Logged in as {self.user} (ID: {self.user.id})\n------')
        await self.change_presence(activity=discord.Game(name="/help"))
