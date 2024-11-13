import discord
from discord import app_commands
from discord.ext import commands

import statalib as lib
import helper


class Help(commands.Cog):
    def __init__(self, client):
        self.client: commands.Bot = client


    @app_commands.command(name="help", description="Help Page")
    @app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
    @app_commands.allowed_installs(guilds=True, users=True)
    async def get_help(self, interaction: discord.Interaction):
        await helper.interactions.run_interaction_checks(interaction)

        embeds = lib.load_embeds('help', color='primary')
        view = lib.shared_views.HelpMenuButtons()
        await interaction.response.send_message(embeds=embeds, view=view)

        lib.update_command_stats(interaction.user.id, 'help')


async def setup(client: commands.Bot) -> None:
    await client.add_cog(Help(client))
