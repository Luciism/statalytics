import os

import discord
from discord import app_commands
from discord.ext import commands

from helper.ui import SelectView
from render.compare import render_compare
from helper.functions import (username_autocompletion,
                       get_command_cooldown,
                       get_hypixel_data,
                       update_command_stats,
                       authenticate_user)


class Compare(commands.Cog):
    def __init__(self, client):
        self.client: discord.Client = client
        self.GENERATING_MESSAGE = 'Generating please wait <a:loading1:1062561739989860462>'


    @app_commands.command(name = "compare", description = "Compare a player's stats to another player's stats")
    @app_commands.autocomplete(player_1=username_autocompletion, player_2=username_autocompletion)
    @app_commands.describe(player_1='The primary player in the comparison', player_2='The secondary player in the comparison')
    @app_commands.checks.dynamic_cooldown(get_command_cooldown)
    async def compare(self, interaction: discord.Interaction, player_1: str, player_2: str=None):
        if player_2 is None:
            try: name_1, uuid_1 = await authenticate_user(None, interaction)
            except TypeError: return
            try: name_2, uuid_2 = await authenticate_user(player_1, interaction)
            except TypeError: return
        else:
            try: name_1, uuid_1 = await authenticate_user(player_1, interaction)
            except TypeError: return
            try: name_2, uuid_2 = await authenticate_user(player_2, interaction)
            except TypeError: return

        await interaction.response.send_message(self.GENERATING_MESSAGE)
        os.makedirs(f'./database/activerenders/{interaction.id}')
        hypixel_data_1 = get_hypixel_data(uuid_1)
        hypixel_data_2 = get_hypixel_data(uuid_2)

        kwargs = {
            "name_1": name_1,
            "name_2": name_2,
            "uuid_1": uuid_1,
            "hypixel_data_1": hypixel_data_1,
            "hypixel_data_2": hypixel_data_2,
            "save_dir": interaction.id
        }

        render_compare(mode="Overall", **kwargs)
        view = SelectView(user=interaction.user.id, inter=interaction, mode='Select a mode')
        await interaction.edit_original_response(content=None, attachments=[discord.File(f"./database/activerenders/{interaction.id}/overall.png")], view=view)
        render_compare(mode="Solos", **kwargs)
        render_compare(mode="Doubles", **kwargs)
        render_compare(mode="Threes", **kwargs)
        render_compare(mode="Fours", **kwargs)
        render_compare(mode="4v4", **kwargs)

        update_command_stats(interaction.user.id, 'compare')


async def setup(client: commands.Bot) -> None:
    await client.add_cog(Compare(client))
