from io import BytesIO

import discord
from discord import app_commands
from discord.ext import commands

import statalib as lib


class Skin(commands.Cog):
    def __init__(self, client):
        self.client: commands.Bot = client


    @app_commands.command(name="skin", description="View the skin of a player")
    @app_commands.autocomplete(player=lib.username_autocompletion)
    @app_commands.describe(player='The player you want to view')
    @app_commands.checks.dynamic_cooldown(lib.generic_command_cooldown)
    async def skin(self, interaction: discord.Interaction, player: str=None):
        await interaction.response.defer()
        await lib.run_interaction_checks(interaction)

        name, uuid = await lib.fetch_player_info(player, interaction)

        image_bytes = await lib.fetch_skin_model(uuid, size=256, style='full')

        embed = discord.Embed(
            title=f"{lib.fname(name)}'s skin",
            url=f"https://namemc.com/profile/{uuid}",
            description=f"Click [here](https://crafatar.com/skins/{uuid}) to download",
            color=lib.get_embed_color('primary')
        )
        embed.set_image(url="attachment://skin.png")

        file = discord.File(BytesIO(image_bytes), filename='skin.png')
        await interaction.followup.send(file=file, embed=embed)

        lib.update_command_stats(interaction.user.id, 'skin')


async def setup(client: commands.Bot) -> None:
    await client.add_cog(Skin(client))
