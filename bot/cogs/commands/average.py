import os

import discord
from discord import app_commands
from discord.ext import commands

from helper.ui import SelectView
from render.average import render_average
from helper.functions import (username_autocompletion,
                       check_subscription,
                       get_hypixel_data,
                       update_command_stats,
                       authenticate_user)


class Average(commands.Cog):
    def __init__(self, client):
        self.client = client
        self.GENERATING_MESSAGE = 'Generating please wait <a:loading1:1062561739989860462>'

    # Average Stats
    @app_commands.command(name = "average", description = "View the average stats of a player")
    @app_commands.autocomplete(username=username_autocompletion)
    @app_commands.describe(username='The player you want to view')
    @app_commands.checks.dynamic_cooldown(check_subscription)
    async def average(self, interaction: discord.Interaction, username: str=None):
        try: name, uuid = await authenticate_user(username, interaction)
        except TypeError: return

        await interaction.response.send_message(self.GENERATING_MESSAGE)
        os.makedirs(f'./database/activerenders/{interaction.id}')
        hypixel_data = get_hypixel_data(uuid)

        render_average(name, uuid, mode="Overall", hypixel_data=hypixel_data, save_dir=interaction.id)
        view = SelectView(user=interaction.user.id, inter=interaction, mode='Select a mode')
        await interaction.edit_original_response(content=None, attachments=[discord.File(f"./database/activerenders/{interaction.id}/overall.png")], view=view)
        render_average(name, uuid, mode="Solos", hypixel_data=hypixel_data, save_dir=interaction.id)
        render_average(name, uuid, mode="Doubles", hypixel_data=hypixel_data, save_dir=interaction.id)
        render_average(name, uuid, mode="Threes", hypixel_data=hypixel_data, save_dir=interaction.id)
        render_average(name, uuid, mode="Fours", hypixel_data=hypixel_data, save_dir=interaction.id)
        render_average(name, uuid, mode="4v4", hypixel_data=hypixel_data, save_dir=interaction.id)

        update_command_stats(interaction.user.id, 'average')

async def setup(client: commands.Bot) -> None:
    await client.add_cog(Average(client))
