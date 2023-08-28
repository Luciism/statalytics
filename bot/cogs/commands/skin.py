from io import BytesIO

import discord
from discord import app_commands
from discord.ext import commands

from statalib import (
    fetch_player_info,
    fetch_skin_model,
    username_autocompletion,
    generic_command_cooldown,
    update_command_stats,
    get_embed_color,
    fname,
)


class Skin(commands.Cog):
    def __init__(self, client):
        self.client: commands.Bot = client


    @app_commands.command(name="skin", description="View the skin of a player")
    @app_commands.autocomplete(player=username_autocompletion)
    @app_commands.describe(player='The player you want to view')
    @app_commands.checks.dynamic_cooldown(generic_command_cooldown)
    async def skin(self, interaction: discord.Interaction, player: str=None):
        await interaction.response.defer()
        name, uuid = await fetch_player_info(player, interaction)

        image_bytes = await fetch_skin_model(uuid, size=256, style='full')

        embed = discord.Embed(
            title=f"{fname(name)}'s skin",
            url=f"https://namemc.com/profile/{uuid}",
            description=f"Click [here](https://crafatar.com/skins/{uuid}) to download",
            color=get_embed_color('primary')
        )
        embed.set_image(url="attachment://skin.png")

        file = discord.File(BytesIO(image_bytes), filename='skin.png')
        await interaction.followup.send(file=file, embed=embed)

        update_command_stats(interaction.user.id, 'skin')


async def setup(client: commands.Bot) -> None:
    await client.add_cog(Skin(client))
