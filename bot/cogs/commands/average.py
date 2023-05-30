import os

import discord
from discord import app_commands
from discord.ext import commands

from helper.ui import SelectView
from render.average import render_average
from helper.functions import (username_autocompletion,
                       get_command_cooldown,
                       get_hypixel_data,
                       update_command_stats,
                       authenticate_user,
                       fetch_skin_model)


class Average(commands.Cog):
    def __init__(self, client):
        self.client: discord.Client = client
        self.GENERATING_MESSAGE = 'Generating please wait <a:loading1:1062561739989860462>'


    @app_commands.command(name = "average", description = "View the average stats of a player")
    @app_commands.autocomplete(username=username_autocompletion)
    @app_commands.describe(username='The player you want to view')
    @app_commands.checks.dynamic_cooldown(get_command_cooldown)
    async def average(self, interaction: discord.Interaction, username: str=None):
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
            "save_dir": interaction.id
        }

        render_average(mode="Overall", **kwargs)
        view = SelectView(user=interaction.user.id, inter=interaction, mode='Select a mode')
        await interaction.edit_original_response(content=None, attachments=[discord.File(f"./database/activerenders/{interaction.id}/overall.png")], view=view)
        render_average(mode="Solos", **kwargs)
        render_average(mode="Doubles", **kwargs)
        render_average(mode="Threes", **kwargs)
        render_average(mode="Fours", **kwargs)
        render_average(mode="4v4", **kwargs)

        update_command_stats(interaction.user.id, 'average')


async def setup(client: commands.Bot) -> None:
    await client.add_cog(Average(client))
