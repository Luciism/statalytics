import discord
from discord.ext import commands

import helper


class CreditsCommandCog(commands.Cog):
    @helper.decorators.app_command("credits")
    @helper.interactions.access_permitted_check()
    async def credits(self, interaction: discord.Interaction):
        embed = helper.Embeds.misc.credits()
        await interaction.response.send_message(embed=embed)


async def setup(client: helper.Client) -> None:
    await client.add_cog(CreditsCommandCog())
