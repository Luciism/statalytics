import logging

import discord
from discord.ext import commands

from statalib.accounts import Account
import helper


logger = logging.getLogger('statalytics')


class CreateAccountCog(commands.Cog):
    @commands.Cog.listener()
    async def on_interaction(self, interaction: discord.Interaction):
        """Create account if it doesnt exist"""
        Account(interaction.user.id).create()


async def setup(client: helper.Client) -> None:
    await client.add_cog(CreateAccountCog())
