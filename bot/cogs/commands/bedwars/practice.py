import discord
from discord import app_commands
from discord.ext import commands

from render.practice import render_practice
from statalib import (
    fetch_player_info,
    username_autocompletion,
    generic_command_cooldown,
    fetch_hypixel_data,
    update_command_stats,
    fetch_skin_model,
    loading_message
)


class Practice(commands.Cog):
    def __init__(self, client):
        self.client: discord.Client = client
        self.LOADING_MSG = loading_message()


    @app_commands.command(name="practice", description="View the practice stats of a player")
    @app_commands.autocomplete(username=username_autocompletion)
    @app_commands.describe(username='The player you want to view')
    @app_commands.checks.dynamic_cooldown(generic_command_cooldown)
    async def practice(self, interaction: discord.Interaction, username: str=None):
        await interaction.response.defer()
        name, uuid = await fetch_player_info(username, interaction)

        await interaction.followup.send(self.LOADING_MSG)

        hypixel_data = await fetch_hypixel_data(uuid)
        skin_res = await fetch_skin_model(uuid, 144)
        rendered = await render_practice(name, uuid, hypixel_data, skin_res)
        await interaction.edit_original_response(content=None, attachments=[discord.File(rendered, filename='practice.png')])

        update_command_stats(interaction.user.id, 'practice')


async def setup(client: commands.Bot) -> None:
    await client.add_cog(Practice(client))
