import os

import discord
from discord import app_commands
from discord.ext import commands

from render.total import render_total
from helper.linking import fetch_player_info
from helper.functions import (
    username_autocompletion,
    get_command_cooldown,
    get_hypixel_data,
    update_command_stats,
    fetch_skin_model,
    send_generic_renders,
    loading_message
)


class Total(commands.Cog):
    def __init__(self, client):
        self.client: discord.Client = client
        self.LOADING_MSG = loading_message()


    async def total_command(self, interaction: discord.Interaction, username: str, method: str):
        await interaction.response.defer()
        name, uuid = await fetch_player_info(username, interaction)

        await interaction.followup.send(self.LOADING_MSG)
        os.makedirs(f'./database/activerenders/{interaction.id}')
        skin_res = await fetch_skin_model(uuid, 144)
        hypixel_data = await get_hypixel_data(uuid)

        kwargs = {
            "name": name,
            "uuid": uuid,
            "hypixel_data": hypixel_data,
            "skin_res": skin_res,
            "save_dir": interaction.id,
            "method": method
        }

        await send_generic_renders(interaction, render_total, kwargs)
        update_command_stats(interaction.user.id, method)


    @app_commands.command(name="bedwars", description="View the general stats of a player")
    @app_commands.autocomplete(username=username_autocompletion)
    @app_commands.describe(username='The player you want to view')
    @app_commands.checks.dynamic_cooldown(get_command_cooldown)
    async def total(self, interaction: discord.Interaction, username: str=None):
        await self.total_command(interaction, username, method='generic')


    @app_commands.command(name="pointless", description="View the general pointless stats of a player")
    @app_commands.autocomplete(username=username_autocompletion)
    @app_commands.describe(username='The player you want to view')
    @app_commands.checks.dynamic_cooldown(get_command_cooldown)
    async def pointless(self, interaction: discord.Interaction, username: str=None):
        await self.total_command(interaction, username, method='pointless')


async def setup(client: commands.Bot) -> None:
    await client.add_cog(Total(client))
