import os

import discord
from discord import app_commands
from discord.ext import commands

from render.compare import render_compare
from statalib import (
    fetch_player_info,
    username_autocompletion,
    generic_command_cooldown,
    fetch_hypixel_data,
    update_command_stats,
    handle_modes_renders,
    loading_message
)


class Compare(commands.Cog):
    def __init__(self, client):
        self.client: discord.Client = client
        self.LOADING_MSG = loading_message()


    @app_commands.command(name="compare", description="Compare a player's stats to another player's stats")
    @app_commands.autocomplete(player_1=username_autocompletion, player_2=username_autocompletion)
    @app_commands.describe(player_1='The primary player in the comparison', player_2='The secondary player in the comparison')
    @app_commands.checks.dynamic_cooldown(generic_command_cooldown)
    async def compare(self, interaction: discord.Interaction, player_1: str, player_2: str=None):
        await interaction.response.defer()
        name_1, uuid_1 = await fetch_player_info(player_1 if player_2 else None, interaction)
        name_2, uuid_2 = await fetch_player_info(player_2 if player_2 else player_1, interaction)

        await interaction.followup.send(self.LOADING_MSG)
        hypixel_data_1 = await fetch_hypixel_data(uuid_1)
        hypixel_data_2 = await fetch_hypixel_data(uuid_2)

        kwargs = {
            "name_1": name_1,
            "name_2": name_2,
            "uuid_1": uuid_1,
            "hypixel_data_1": hypixel_data_1,
            "hypixel_data_2": hypixel_data_2,
            "save_dir": interaction.id
        }

        await handle_modes_renders(interaction, render_compare, kwargs)
        update_command_stats(interaction.user.id, 'compare')


async def setup(client: commands.Bot) -> None:
    await client.add_cog(Compare(client))
