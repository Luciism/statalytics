import discord
from discord import app_commands
from discord.ext import commands

from render.cosmetics import render_cosmetics
from functions import (username_autocompletion,
                       check_subscription,
                       get_hypixel_data,
                       update_command_stats,
                       authenticate_user)


class Cosmetics(commands.Cog):
    def __init__(self, client):
        self.client = client
        self.GENERATING_MESSAGE = 'Generating please wait <a:loading1:1062561739989860462>'

    # Active Cosmetics
    @app_commands.command(name = "activecosmetics", description = "View the practice stats of a player")
    @app_commands.autocomplete(username=username_autocompletion)
    @app_commands.describe(username='The player you want to view')
    @app_commands.checks.dynamic_cooldown(check_subscription)
    async def active_cosmetics(self, interaction: discord.Interaction, username: str=None):
        try: name, uuid = await authenticate_user(username, interaction)
        except TypeError: return

        await interaction.response.send_message(self.GENERATING_MESSAGE)

        hypixel_data = get_hypixel_data(uuid)
        rendered = render_cosmetics(name, uuid, hypixel_data)
        await interaction.edit_original_response(content=None, attachments=[discord.File(rendered, filename='cosmetics.png')])

        update_command_stats(interaction.user.id, 'cosmetics')

async def setup(client: commands.Bot) -> None:
    await client.add_cog(Cosmetics(client))
