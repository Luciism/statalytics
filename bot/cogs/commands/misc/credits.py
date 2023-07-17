import discord
from discord import app_commands
from discord.ext import commands

from statalib.functions import update_command_stats, load_embeds


class Credits(commands.Cog):
    def __init__(self, client):
        self.client: discord.Client = client


    @app_commands.command(name="credits", description="The people who made Statalytics possible")
    async def credits(self, interaction: discord.Interaction):
        embeds = load_embeds('credits', color='primary')
        await interaction.response.send_message(embeds=embeds)

        update_command_stats(interaction.user.id, 'credits')


async def setup(client: commands.Bot) -> None:
    await client.add_cog(Credits(client))
