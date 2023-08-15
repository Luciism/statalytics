import discord
from discord import app_commands
from discord.ext import commands

from render.total import render_total
from render.pointless import render_pointless
from statalib import (
    fetch_player_info,
    username_autocompletion,
    generic_command_cooldown,
    fetch_hypixel_data,
    update_command_stats,
    fetch_skin_model,
    handle_modes_renders,
    loading_message
)


class Total(commands.Cog):
    def __init__(self, client):
        self.client: discord.Client = client
        self.LOADING_MSG = loading_message()


    async def total_command(self, interaction: discord.Interaction,
                            player: str, method: str):
        await interaction.response.defer()

        name, uuid = await fetch_player_info(player, interaction)

        await interaction.followup.send(self.LOADING_MSG)
        skin_res = await fetch_skin_model(uuid, 144)
        hypixel_data = await fetch_hypixel_data(uuid)

        kwargs = {
            "name": name,
            "uuid": uuid,
            "hypixel_data": hypixel_data,
            "skin_res": skin_res,
            "save_dir": interaction.id
        }

        if method == 'generic':
            await handle_modes_renders(interaction, render_total, kwargs)
        else:
            await handle_modes_renders(interaction, render_pointless, kwargs)
        update_command_stats(interaction.user.id, method)


    @app_commands.command(
        name="bedwars",
        description="View the general stats of a player")
    @app_commands.describe(player='The player you want to view')
    @app_commands.autocomplete(player=username_autocompletion)
    @app_commands.checks.dynamic_cooldown(generic_command_cooldown)
    async def total(self, interaction: discord.Interaction, player: str=None):
        await self.total_command(interaction, player, method='generic')


    @app_commands.command(
        name="pointless",
        description="View the general pointless stats of a player")
    @app_commands.describe(player='The player you want to view')
    @app_commands.autocomplete(player=username_autocompletion)
    @app_commands.checks.dynamic_cooldown(generic_command_cooldown)
    async def pointless(self, interaction: discord.Interaction,
                        player: str=None):
        await self.total_command(interaction, player, method='pointless')


async def setup(client: commands.Bot) -> None:
    await client.add_cog(Total(client))
