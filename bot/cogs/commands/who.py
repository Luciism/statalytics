import discord
from discord import app_commands
from discord.ext import commands

from mcuuid import MCUUID
from functions import update_command_stats

class Who(commands.Cog):
    def __init__(self, client):
        self.client = client

    @app_commands.command(name = "who", description = "Convert the name of uuid of a player")
    @app_commands.describe(username_or_uuid='The player whos username / uuid you want to view')
    async def who(self, interaction: discord.Interaction, username_or_uuid: str):
        if len(username_or_uuid) < 16:
            try:
                name = MCUUID(name=username_or_uuid).name
                uuid = MCUUID(name=username_or_uuid).uuid
                await interaction.response.send_message(f'UUID for **{name}** -> `{uuid}`', ephemeral=True)
            except KeyError:
                await interaction.response.send_message('Invalid name or uuid!', ephemeral=True)
        else:
            name = MCUUID(uuid=username_or_uuid).name
            uuid = MCUUID(uuid=username_or_uuid).uuid
            if name: await interaction.response.send_message(f'Name for **{uuid}** -> `{name}`', ephemeral=True)
            else: await interaction.response.send_message('Invalid name or uuid!', ephemeral=True)

        update_command_stats(interaction.user.id, 'who')

async def setup(client: commands.Bot) -> None:
    await client.add_cog(Who(client))
