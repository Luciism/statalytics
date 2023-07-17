from io import BytesIO
from requests import ConnectTimeout, ReadTimeout

import discord
from discord import app_commands
from discord.ext import commands

from statalib import (
    fetch_player_info,
    username_autocompletion,
    generic_command_cooldown,
    update_command_stats,
    to_thread,
    load_embeds,
    skin_session
)


class Skin(commands.Cog):
    def __init__(self, client):
        self.client: discord.Client = client


    @to_thread
    def fetch_skin(self, uuid):
        return skin_session.get(f'https://visage.surgeplay.com/full/{uuid}', timeout=5).content


    @app_commands.command(name="skin", description="View the skin of a player")
    @app_commands.autocomplete(username=username_autocompletion)
    @app_commands.describe(username='The player you want to view')
    @app_commands.checks.dynamic_cooldown(generic_command_cooldown)
    async def skin(self, interaction: discord.Interaction, username: str=None):
        await interaction.response.defer()
        name, uuid = await fetch_player_info(username, interaction)

        refined = name.replace('_', r'\_')

        try:
            image_bytes = await self.fetch_skin(uuid)
        except (ReadTimeout, ConnectTimeout):
            await interaction.followup.send('Failed to fetch skin, please try again later. (Skin API error)')
            return

        format_values = {
            'username': refined,
            'uuid': uuid
        }
        embeds = load_embeds('skin', format_values, color='primary')
        file = discord.File(BytesIO(image_bytes), filename='skin.png')
        await interaction.followup.send(file=file, embeds=embeds)

        update_command_stats(interaction.user.id, 'skin')


async def setup(client: commands.Bot) -> None:
    await client.add_cog(Skin(client))
