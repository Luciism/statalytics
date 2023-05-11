from io import BytesIO
from json import load as load_json

import discord
from discord import app_commands
from discord.ext import commands

from functions import (username_autocompletion,
                       check_subscription,
                       update_command_stats,
                       authenticate_user,
                       skin_session)


class Skin(commands.Cog):
    def __init__(self, client):
        self.client = client
        self.GENERATING_MESSAGE = 'Generating please wait <a:loading1:1062561739989860462>'

    # Skin View
    @app_commands.command(name = "skin", description = "View the skin of a player")
    @app_commands.autocomplete(username=username_autocompletion)
    @app_commands.describe(username='The player you want to view')
    @app_commands.checks.dynamic_cooldown(check_subscription)
    async def skin(self, interaction: discord.Interaction, username: str=None):
        try: name, uuid = await authenticate_user(username, interaction)
        except TypeError: return

        refined = name.replace('_', r'\_')
        image_bytes = skin_session.get(f'https://visage.surgeplay.com/full/{uuid}', timeout=10).content
        file = discord.File(BytesIO(image_bytes), filename='skin.png')

        with open('./config.json', 'r') as datafile:
            config = load_json(datafile)
        embed_color = int(config['embed_primary_color'], base=16)
        embed = discord.Embed(title=f"{refined}'s skin", url= f"https://namemc.com/profile/{uuid}", description=f"Click [here](https://crafatar.com/skins/{uuid}) to download", color=embed_color)
        embed.set_image(url="attachment://skin.png")
        await interaction.response.send_message(file=file, embed=embed)

        update_command_stats(interaction.user.id, 'skin')

async def setup(client: commands.Bot) -> None:
    await client.add_cog(Skin(client))
