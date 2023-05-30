import json

import discord
from discord import app_commands
from discord.ext import commands


class ResetTime(commands.Cog):
    def __init__(self, client):
        self.client: discord.Client = client


    @app_commands.command(name="resettime", description="[DEPRECATED USE /settings] Configure the reset timezone for historical stats (GMT)")
    async def reset_time(self, interaction: discord.Interaction):
        with open('./config.json', 'r') as datafile:
            config = json.load(datafile)

        embed_color = int(config['embed_danger_color'], base=16)
        embed = discord.Embed(
            title='This command is DEPRECATED!',
            description='In order to configure your reset time, please use `/settings`!\nThis command will be removed in the near future!',
            color=embed_color
        )
        await interaction.response.send_message(embed=embed)


async def setup(client: commands.Bot) -> None:
    await client.add_cog(ResetTime(client))
