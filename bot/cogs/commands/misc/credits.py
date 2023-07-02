from json import load as load_json

import discord
from discord import app_commands
from discord.ext import commands

from helper.functions import update_command_stats


class Credits(commands.Cog):
    def __init__(self, client):
        self.client: discord.Client = client


    @app_commands.command(name="credits", description="The people who made Statalytics possible")
    async def credits(self, interaction: discord.Interaction):
        with open('./assets/embeds/credits.json', 'r') as datafile:
            credits = load_json(datafile)

        embeds = [discord.Embed.from_dict(embed) for embed in credits['embeds']]
        await interaction.response.send_message(embeds=embeds)

        update_command_stats(interaction.user.id, 'credits')


async def setup(client: commands.Bot) -> None:
    await client.add_cog(Credits(client))
