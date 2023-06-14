from io import BytesIO
from requests import ConnectTimeout, ReadTimeout

import discord
from discord import app_commands
from discord.ext import commands

from helper.functions import (
    username_autocompletion,
    get_command_cooldown,
    update_command_stats,
    authenticate_user,
    get_embed_color,
    to_thread,
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
    @app_commands.checks.dynamic_cooldown(get_command_cooldown)
    async def skin(self, interaction: discord.Interaction, username: str=None):
        await interaction.response.defer()
        try: name, uuid = await authenticate_user(username, interaction)
        except TypeError: return

        refined = name.replace('_', r'\_')

        try:
            image_bytes = await self.fetch_skin(uuid)
        except (ReadTimeout, ConnectTimeout):
            await interaction.followup.send('Failed to fetch skin, please try again later. (Skin API error)')
            return

        file = discord.File(BytesIO(image_bytes), filename='skin.png')

        embed_color = get_embed_color('primary')
        embed = discord.Embed(
            title=f"{refined}'s skin",
            url=f"https://namemc.com/profile/{uuid}",
            description=f"Click [here](https://crafatar.com/skins/{uuid}) to download",
            color=embed_color
        )
        embed.set_image(url="attachment://skin.png")
        await interaction.followup.send(file=file, embed=embed)

        update_command_stats(interaction.user.id, 'skin')


async def setup(client: commands.Bot) -> None:
    await client.add_cog(Skin(client))
