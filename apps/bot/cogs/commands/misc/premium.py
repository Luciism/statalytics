import discord
from discord.ext import commands

import helper


class PremiumCommandCog(commands.Cog):
    @helper.decorators.app_command("premium")
    @helper.interactions.access_permitted_check()
    async def premium_command(self, interaction: discord.Interaction):
        await interaction.response.defer()

        await interaction.followup.send(
            embed=helper.Embeds.premium.premium(),
            view=helper.views.PremiumInfoView()
        )


async def setup(client: helper.Client) -> None:
    await client.add_cog(PremiumCommandCog())
