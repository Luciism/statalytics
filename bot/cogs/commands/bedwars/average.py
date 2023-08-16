import discord
from discord import app_commands
from discord.ext import commands

from render.average import render_average
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


class Average(commands.Cog):
    def __init__(self, client):
        self.client: commands.Bot = client
        self.LOADING_MSG = loading_message()


    @app_commands.command(
        name="average",
        description="View the average stats of a player")
    @app_commands.describe(player='The player you want to view')
    @app_commands.autocomplete(player=username_autocompletion)
    @app_commands.checks.dynamic_cooldown(generic_command_cooldown)
    async def average(self, interaction: discord.Interaction, player: str=None):
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

        await handle_modes_renders(interaction, render_average, kwargs)
        update_command_stats(interaction.user.id, 'average')


async def setup(client: commands.Bot) -> None:
    await client.add_cog(Average(client))
