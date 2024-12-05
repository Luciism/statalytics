import discord
from discord import app_commands
from discord.ext import commands

import statalib as lib
import helper
from render.displayname import render_displayname


class DisplayName(commands.Cog):
    def __init__(self, client):
        self.client: commands.Bot = client


    @app_commands.command(
        name="displayname",
        description="Render the bedwars display name of any player")
    @app_commands.describe(player='The player whos display name to generate')
    @app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
    @app_commands.allowed_installs(guilds=True, users=True)
    @app_commands.checks.dynamic_cooldown(helper.generic_command_cooldown)
    @app_commands.autocomplete(player=helper.username_autocompletion)
    async def displayname(self, interaction: discord.Interaction,
                          player: str=None):
        await interaction.response.defer()
        await helper.interactions.run_interaction_checks(interaction)

        name, uuid = await helper.interactions.fetch_player_info(player, interaction)
        hypixel_data = await lib.network.fetch_hypixel_data(uuid)

        if not hypixel_data.get('player'):
            hypixel_data['player'] = {}

        rendered = await render_displayname(name, hypixel_data)
        await interaction.followup.send(
            content=None,
            files=[discord.File(rendered, filename="displayname.png")]
        )

        lib.usage.update_command_stats(interaction.user.id, 'displayname')


async def setup(client: commands.Bot) -> None:
    await client.add_cog(DisplayName(client))
