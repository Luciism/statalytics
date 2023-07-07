import discord
from discord import app_commands
from discord.ext import commands

from helper.functions import update_command_stats, load_embeds


class Help(commands.Cog):
    def __init__(self, client):
        self.client: discord.Client = client


    @app_commands.command(name="help", description="Help Page")
    async def get_help(self, interaction: discord.Interaction):
        embeds = load_embeds('help', color='primary')
        await interaction.response.send_message(embeds=embeds, ephemeral=True)

        update_command_stats(interaction.user.id, 'help')


async def setup(client: commands.Bot) -> None:
    await client.add_cog(Help(client))
