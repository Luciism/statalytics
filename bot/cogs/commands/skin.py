from io import BytesIO
from requests import ConnectTimeout, ReadTimeout

import discord
from discord import app_commands
from discord.ext import commands

from helper.functions import (username_autocompletion,
                            get_command_cooldown,
                            update_command_stats,
                            authenticate_user,
                            get_embed_color,
                            skin_session)


class Skin(commands.Cog):
    def __init__(self, client):
        self.client: discord.Client = client


    @app_commands.command(name = "skin", description = "View the skin of a player")
    @app_commands.autocomplete(username=username_autocompletion)
    @app_commands.describe(username='The player you want to view')
    @app_commands.checks.dynamic_cooldown(get_command_cooldown)
    async def skin(self, interaction: discord.Interaction, username: str=None):
        await interaction.response.defer()
        try: name, uuid = await authenticate_user(username, interaction)
        except TypeError: return

        refined = name.replace('_', r'\_')
        image_bytes = skin_session.get(f'https://visage.surgeplay.com/full/{uuid}', timeout=5).content
        file = discord.File(BytesIO(image_bytes), filename='skin.png')

        try:
            image_bytes = skin_session.get(f'https://visage.surgeplay.com/full/{uuid}', timeout=5).content
        except (ReadTimeout, ConnectTimeout):
            await interaction.followup.send('Failed to fetch skin, please try again later. (Skin API error)')
            return

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
