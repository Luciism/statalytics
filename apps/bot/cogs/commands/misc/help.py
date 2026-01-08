import discord
from discord.ext import commands

import helper


class HelpCommandCog(commands.Cog):
    @helper.decorators.app_command("help")
    @helper.interactions.access_permitted_check()
    async def help(self, interaction: discord.Interaction):
        embed = helper.Embeds.help.help()
        view = helper.views.info.HelpMenuButtons()
        await interaction.response.send_message(embed=embed, view=view)


async def setup(client: helper.Client) -> None:
    await client.add_cog(HelpCommandCog())
