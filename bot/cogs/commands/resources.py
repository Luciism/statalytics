import os

import discord
from discord import app_commands
from discord.ext import commands

from helper.ui import SelectView
from render.resources import render_resources
from helper.functions import (username_autocompletion,
                       get_command_cooldown,
                       get_hypixel_data,
                       update_command_stats,
                       authenticate_user)


class Resources(commands.Cog):
    def __init__(self, client):
        self.client: discord.Client = client
        self.GENERATING_MESSAGE = 'Generating please wait <a:loading1:1062561739989860462>'


    @app_commands.command(name = "resources", description = "View the resource stats of a player")
    @app_commands.autocomplete(username=username_autocompletion)
    @app_commands.describe(username='The player you want to view')
    @app_commands.checks.dynamic_cooldown(get_command_cooldown)
    async def resources(self, interaction: discord.Interaction, username: str=None):
        try: name, uuid = await authenticate_user(username, interaction)
        except TypeError: return

        await interaction.response.send_message(self.GENERATING_MESSAGE)
        os.makedirs(f'./database/activerenders/{interaction.id}')
        hypixel_data = get_hypixel_data(uuid)

        kwargs = {
            "name": name,
            "uuid": uuid,
            "hypixel_data": hypixel_data,
            "save_dir": interaction.id
        }

        render_resources(mode="Overall", **kwargs)
        view = SelectView(user=interaction.user.id, inter=interaction, mode='Select a mode')
        await interaction.edit_original_response(content=None, attachments=[discord.File(f"./database/activerenders/{interaction.id}/overall.png")], view=view)
        render_resources(mode="Solos", **kwargs)
        render_resources(mode="Doubles", **kwargs)
        render_resources(mode="Threes", **kwargs)
        render_resources(mode="Fours", **kwargs)
        render_resources(mode="4v4", **kwargs)

        update_command_stats(interaction.user.id, 'resources')


async def setup(client: commands.Bot) -> None:
    await client.add_cog(Resources(client))
