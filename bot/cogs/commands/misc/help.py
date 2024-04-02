import discord
from discord import app_commands
from discord.ext import commands

import statalib as lib


class Help(commands.Cog):
    def __init__(self, client):
        self.client: commands.Bot = client


    @app_commands.command(name="help", description="Help Page")
    async def get_help(self, interaction: discord.Interaction):
        await lib.run_interaction_checks(interaction)

        embeds = lib.load_embeds('help', color='primary')
        view = lib.HelpMenuButtons()
        await interaction.response.send_message(embeds=embeds, view=view)

        lib.update_command_stats(interaction.user.id, 'help')


async def setup(client: commands.Bot) -> None:
    await client.add_cog(Help(client))
