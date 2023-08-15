import discord
from discord import app_commands
from discord.ext import commands

from render.cosmetics import render_cosmetics
from statalib import (
    fetch_player_info,
    username_autocompletion,
    generic_command_cooldown,
    fetch_hypixel_data,
    update_command_stats,
    loading_message
)


class Cosmetics(commands.Cog):
    def __init__(self, client):
        self.client: discord.Client = client
        self.LOADING_MSG = loading_message()


    @app_commands.command(
        name="activecosmetics",
        description="View the practice stats of a player")
    @app_commands.describe(player='The player you want to view')
    @app_commands.autocomplete(player=username_autocompletion)
    @app_commands.checks.dynamic_cooldown(generic_command_cooldown)
    async def active_cosmetics(self, interaction: discord.Interaction,
                               player: str=None):
        await interaction.response.defer()

        name, uuid = await fetch_player_info(player, interaction)

        await interaction.followup.send(self.LOADING_MSG)

        hypixel_data = await fetch_hypixel_data(uuid)
        rendered = await render_cosmetics(name, uuid, hypixel_data)

        await interaction.edit_original_response(
            content=None,
            attachments=[discord.File(rendered, filename='cosmetics.png')]
        )

        update_command_stats(interaction.user.id, 'cosmetics')


async def setup(client: commands.Bot) -> None:
    await client.add_cog(Cosmetics(client))
