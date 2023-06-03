import os

import discord
from discord import app_commands
from discord.ext import commands

from helper.ui import ModesView
from render.total import render_total
from helper.functions import (username_autocompletion,
                       get_command_cooldown,
                       get_hypixel_data,
                       update_command_stats,
                       authenticate_user,
                       fetch_skin_model)


class Total(commands.Cog):
    def __init__(self, client):
        self.client: discord.Client = client
        self.GENERATING_MESSAGE = 'Generating please wait <a:loading1:1062561739989860462>'


    async def total_command(self, interaction: discord.Interaction, username: str, method: str):
        try: name, uuid = await authenticate_user(username, interaction)
        except TypeError: return

        await interaction.response.send_message(self.GENERATING_MESSAGE)
        os.makedirs(f'./database/activerenders/{interaction.id}')
        skin_res = fetch_skin_model(uuid, 144)
        hypixel_data = get_hypixel_data(uuid)

        kwargs = {
            "name": name,
            "uuid": uuid,
            "hypixel_data": hypixel_data,
            "skin_res": skin_res,
            "save_dir": interaction.id,
            "method": method
        }

        render_total(mode="Overall", **kwargs)
        view = ModesView(user=interaction.user.id, inter=interaction, mode='Select a mode')
        await interaction.edit_original_response(
            content=None, attachments=[discord.File(f"./database/activerenders/{interaction.id}/overall.png")], view=view)

        render_total(mode="Solos", **kwargs)
        render_total(mode="Doubles", **kwargs)
        render_total(mode="Threes", **kwargs)
        render_total(mode="Fours", **kwargs)
        render_total(mode="4v4", **kwargs)

        update_command_stats(interaction.user.id, method)


    @app_commands.command(name = "bedwars", description = "View the general stats of a player")
    @app_commands.autocomplete(username=username_autocompletion)
    @app_commands.describe(username='The player you want to view')
    @app_commands.checks.dynamic_cooldown(get_command_cooldown)
    async def total(self, interaction: discord.Interaction, username: str=None):
        await self.total_command(interaction, username, method='generic')


    @app_commands.command(name = "pointless", description = "View the general pointless stats of a player")
    @app_commands.autocomplete(username=username_autocompletion)
    @app_commands.describe(username='The player you want to view')
    @app_commands.checks.dynamic_cooldown(get_command_cooldown)
    async def pointless(self, interaction: discord.Interaction, username: str=None):
        await self.total_command(interaction, username, method='pointless')


async def setup(client: commands.Bot) -> None:
    await client.add_cog(Total(client))
