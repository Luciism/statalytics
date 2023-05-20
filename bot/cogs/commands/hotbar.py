import discord
from discord import app_commands
from discord.ext import commands

from render.hotbar import render_hotbar
from functions import (username_autocompletion,
                       check_subscription,
                       get_hypixel_data,
                       update_command_stats,
                       authenticate_user)


class Hotbar(commands.Cog):
    def __init__(self, client):
        self.client = client
        self.GENERATING_MESSAGE = 'Generating please wait <a:loading1:1062561739989860462>'

    # Hotbar
    @app_commands.command(name = "hotbar", description = "View the hotbar preferences of a player")
    @app_commands.autocomplete(username=username_autocompletion)
    @app_commands.describe(username='The player you want to view')
    @app_commands.checks.dynamic_cooldown(check_subscription)
    async def hotbar(self, interaction: discord.Interaction,username: str=None):
        try: name, uuid = await authenticate_user(username, interaction)
        except TypeError: return

        refined = name.replace('_', r'\_')
        await interaction.response.send_message(self.GENERATING_MESSAGE)

        hypixel_data = get_hypixel_data(uuid)
        rendered = render_hotbar(name, uuid, hypixel_data)
        if rendered is not False:
            await interaction.edit_original_response(content=None, attachments=[discord.File(rendered, filename="hotbar.png")])
        else: await interaction.edit_original_response(content=f'**{refined}** does not have a hotbar set!**')

        update_command_stats(interaction.user.id, 'hotbar')

async def setup(client: commands.Bot) -> None:
    await client.add_cog(Hotbar(client))
