import discord
from discord import app_commands
from discord.ext import commands

from helper.linking import fetch_player_info
from helper.functions import update_command_stats


class Who(commands.Cog):
    def __init__(self, client):
        self.client: discord.Client = client


    @app_commands.command(name="who", description="Convert the name of uuid of a player")
    @app_commands.describe(username_or_uuid='The player whos username / uuid you want to view')
    async def who(self, interaction: discord.Interaction, username_or_uuid: str=None):
        name, uuid = await fetch_player_info(username_or_uuid, interaction, eph=True)

        if username_or_uuid is None or len(username_or_uuid) < 16:
            await interaction.response.send_message(f'UUID for **{name}** -> `{uuid}`', ephemeral=True)
        else:
            await interaction.response.send_message(f'Name for **{uuid}** -> `{name}`', ephemeral=True)

        update_command_stats(interaction.user.id, 'who')


async def setup(client: commands.Bot) -> None:
    await client.add_cog(Who(client))
