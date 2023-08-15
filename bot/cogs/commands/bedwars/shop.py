import discord
from discord import app_commands
from discord.ext import commands

from render.shop import render_shop
from statalib import (
    fetch_player_info,
    username_autocompletion,
    generic_command_cooldown,
    fetch_hypixel_data,
    update_command_stats,
    loading_message
)


class Shop(commands.Cog):
    def __init__(self, client):
        self.client: discord.Client = client
        self.LOADING_MSG = loading_message()


    @app_commands.command(
        name="shop",
        description="View the shopkeeper of a player")
    @app_commands.describe(player='The player you want to view')
    @app_commands.autocomplete(player=username_autocompletion)
    @app_commands.checks.dynamic_cooldown(generic_command_cooldown)
    async def shop(self, interaction: discord.Interaction, player: str=None):
        await interaction.response.defer()
        name, uuid = await fetch_player_info(player, interaction)

        await interaction.followup.send(self.LOADING_MSG)

        hypixel_data = await fetch_hypixel_data(uuid)

        rendered = await render_shop(name, uuid, hypixel_data)

        await interaction.edit_original_response(
            content=None,
            attachments=[discord.File(rendered, filename="shop.png")]
        )

        update_command_stats(interaction.user.id, 'shop')


async def setup(client: commands.Bot) -> None:
    await client.add_cog(Shop(client))
