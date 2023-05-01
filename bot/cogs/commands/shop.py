import os
import sqlite3

import discord
from discord import app_commands
from discord.ext import commands

from render.rendershop import rendershop
from functions import (username_autocompletion,
                       check_subscription,
                       get_hypixel_data,
                       update_command_stats,
                       authenticate_user)


class Shop(commands.Cog):
    def __init__(self, client):
        self.client = client
        self.GENERATING_MESSAGE = 'Generating please wait <a:loading1:1062561739989860462>'

    # Shopkeeper
    @app_commands.command(name = "shop", description = "View the shopkeeper of a player")
    @app_commands.autocomplete(username=username_autocompletion)
    @app_commands.describe(username='The player you want to view')
    @app_commands.checks.dynamic_cooldown(check_subscription)
    async def shop(self, interaction: discord.Interaction,username: str=None):
        try: name, uuid = await authenticate_user(username, interaction)
        except TypeError: return

        refined = name.replace('_', r'\_')
        await interaction.response.send_message(self.GENERATING_MESSAGE)

        hypixel_data = get_hypixel_data(uuid)
        rendered = rendershop(uuid, hypixel_data)
        if rendered is not False:
            await interaction.edit_original_response(content=None, attachments=[discord.File(rendered, filename="shop.png")])
        else: await interaction.edit_original_response(content=f'**{refined}** has not played before!')

        update_command_stats(interaction.user.id, 'shop')

async def setup(client: commands.Bot) -> None:
    await client.add_cog(Shop(client))
