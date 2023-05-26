import discord
from discord import app_commands
from discord.ext import commands

from render.displayname import render_displayname
from helper.functions import check_subscription, username_autocompletion, authenticate_user, get_hypixel_data, update_command_stats

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
        if not hypixel_data.get('player'):
            hypixel_data['player'] = {}
        rendered = render_displayname(name, hypixel_data)
        await interaction.followup.send(content=None, files=[discord.File(rendered, filename="displayname.png")])

        update_command_stats(interaction.user.id, 'displayname')

async def setup(client: commands.Bot) -> None:
    await client.add_cog(DisplayName(client))
