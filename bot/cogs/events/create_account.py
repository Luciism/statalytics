import logging

import discord
from discord.ext import commands

from statalib import create_account


logger = logging.getLogger('statalytics')


class CreateAccount(commands.Cog):
    def __init__(self, client):
        self.client: commands.Bot = client


    @commands.Cog.listener()
    async def on_interaction(self, interaction: discord.Interaction):
        """Create account if it doesnt exist"""
        # logger.debug(
        #     f'Created account for {interaction.user} ({interaction.user.id})')
        create_account(interaction.user.id)


async def setup(client: commands.Bot) -> None:
    await client.add_cog(CreateAccount(client))
