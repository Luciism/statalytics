import discord
from discord import app_commands
from discord.ext import commands

from statalib import (
    HelpMenuButtons,
    update_command_stats,
    load_embeds,
    run_interaction_checks
)


class Help(commands.Cog):
    def __init__(self, client):
        self.client: commands.Bot = client


    @app_commands.command(name="help", description="Help Page")
    async def get_help(self, interaction: discord.Interaction):
        await run_interaction_checks(interaction)

        embeds = load_embeds('help', color='primary')
        view = HelpMenuButtons()
        await interaction.response.send_message(embeds=embeds, view=view)

        update_command_stats(interaction.user.id, 'help')


async def setup(client: commands.Bot) -> None:
    await client.add_cog(Help(client))
