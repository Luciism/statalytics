import os

import discord
from discord import app_commands
from discord.ext import commands

from render.average import render_average
from helper.functions import (
    username_autocompletion,
    get_command_cooldown,
    get_hypixel_data,
    update_command_stats,
    authenticate_user,
    fetch_skin_model,
    send_generic_renders,
    loading_message
)


class Average(commands.Cog):
    def __init__(self, client):
        self.client: discord.Client = client
        self.LOADING_MSG = loading_message()


    @app_commands.command(name="average", description="View the average stats of a player")
    @app_commands.autocomplete(username=username_autocompletion)
    @app_commands.describe(username='The player you want to view')
    @app_commands.checks.dynamic_cooldown(get_command_cooldown)
    async def average(self, interaction: discord.Interaction, username: str=None):
        await interaction.response.defer()
        try: name, uuid = await authenticate_user(username, interaction)
        except TypeError: return

        await interaction.followup.send(self.LOADING_MSG)
        os.makedirs(f'./database/activerenders/{interaction.id}')
        skin_res = await fetch_skin_model(uuid, 144)
        hypixel_data = await get_hypixel_data(uuid)

        kwargs = {
            "name": name,
            "uuid": uuid,
            "hypixel_data": hypixel_data,
            "skin_res": skin_res,
            "save_dir": interaction.id
        }

        await send_generic_renders(interaction, render_average, kwargs)
        update_command_stats(interaction.user.id, 'average')


async def setup(client: commands.Bot) -> None:
    await client.add_cog(Average(client))
