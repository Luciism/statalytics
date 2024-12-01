import logging

import discord
from discord.ext import commands

from statalib.accounts import Account


logger = logging.getLogger('statalytics')


class CreateAccount(commands.Cog):
    def __init__(self, client):
        self.client: commands.Bot = client


    @commands.Cog.listener()
    async def on_interaction(self, interaction: discord.Interaction):
        """Create account if it doesnt exist"""
        # logger.debug(
        #     f'Created account for {interaction.user} ({interaction.user.id})')
        Account(interaction.user.id).create()


async def setup(client: commands.Bot) -> None:
    await client.add_cog(CreateAccount(client))
