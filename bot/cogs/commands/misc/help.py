from json import load as load_json

import discord
from discord import app_commands
from discord.ext import commands

from helper.functions import update_command_stats


class Help(commands.Cog):
    def __init__(self, client):
        self.client: discord.Client = client


    @app_commands.command(name="help", description="Help Page")
    async def get_help(self, interaction: discord.Interaction):
        with open('./assets/embeds/help.json', 'r') as datafile:
            embed_data = load_json(datafile)

        embeds = [discord.Embed.from_dict(embed) for embed in embed_data['embeds']]
        await interaction.response.send_message(embeds=embeds, ephemeral=True)

        update_command_stats(interaction.user.id, 'help')


async def setup(client: commands.Bot) -> None:
    await client.add_cog(Help(client))
