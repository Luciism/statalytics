import discord
from discord import app_commands
from discord.ext import commands

from render.practice import render_practice
from helper.functions import (username_autocompletion,
                       get_command_cooldown,
                       get_hypixel_data,
                       update_command_stats,
                       authenticate_user,
                       fetch_skin_model)


class Practice(commands.Cog):
    def __init__(self, client):
        self.client: discord.Client = client
        self.GENERATING_MESSAGE = 'Generating please wait <a:loading1:1062561739989860462>'


    @app_commands.command(name = "practice", description = "View the practice stats of a player")
    @app_commands.autocomplete(username=username_autocompletion)
    @app_commands.describe(username='The player you want to view')
    @app_commands.checks.dynamic_cooldown(get_command_cooldown)
    async def practice(self, interaction: discord.Interaction, username: str=None):
        try: name, uuid = await authenticate_user(username, interaction)
        except TypeError: return

        await interaction.response.send_message(self.GENERATING_MESSAGE)

        hypixel_data = get_hypixel_data(uuid)
        skin_res = fetch_skin_model(uuid, 144)
        rendered = render_practice(name, uuid, hypixel_data, skin_res)
        await interaction.edit_original_response(content=None, attachments=[discord.File(rendered, filename='practice.png')])

        update_command_stats(interaction.user.id, 'practice')


async def setup(client: commands.Bot) -> None:
    await client.add_cog(Practice(client))
