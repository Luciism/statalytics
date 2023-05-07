import discord
from discord import app_commands
from discord.ext import commands

from render.renderdisplayname import renderdisplayname
from functions import check_subscription, username_autocompletion, authenticate_user, get_hypixel_data

class DisplayName(commands.Cog):
    def __init__(self, client):
        self.client = client

    @app_commands.command(name = "displayname", description = "Render the bedwars display name of any player")
    @app_commands.checks.dynamic_cooldown(check_subscription)
    @app_commands.autocomplete(username=username_autocompletion)
    @app_commands.describe(username='The player whos display name to generate')
    async def displayname(self, interaction: discord.Interaction, username: str=None):
        try: name, uuid = await authenticate_user(username, interaction)
        except TypeError: return

        await interaction.response.defer()
        hypixel_data = get_hypixel_data(uuid)
        rendered = renderdisplayname(name, hypixel_data)
        await interaction.followup.send(content=None, files=[discord.File(rendered, filename="displayname.png")])

async def setup(client: commands.Bot) -> None:
    await client.add_cog(DisplayName(client))
