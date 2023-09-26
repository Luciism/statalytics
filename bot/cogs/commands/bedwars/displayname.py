import discord
from discord import app_commands
from discord.ext import commands

from render.displayname import render_displayname
from statalib import (
    fetch_player_info,
    generic_command_cooldown,
    username_autocompletion,
    fetch_hypixel_data,
    update_command_stats,
    run_interaction_checks
)


class DisplayName(commands.Cog):
    def __init__(self, client):
        self.client: commands.Bot = client


    @app_commands.command(
        name="displayname",
        description="Render the bedwars display name of any player")
    @app_commands.describe(player='The player whos display name to generate')
    @app_commands.checks.dynamic_cooldown(generic_command_cooldown)
    @app_commands.autocomplete(player=username_autocompletion)
    async def displayname(self, interaction: discord.Interaction,
                          player: str=None):
        await interaction.response.defer()
        await run_interaction_checks(interaction)

        name, uuid = await fetch_player_info(player, interaction)
        hypixel_data = await fetch_hypixel_data(uuid)

        if not hypixel_data.get('player'):
            hypixel_data['player'] = {}

        rendered = await render_displayname(name, hypixel_data)
        await interaction.followup.send(
            content=None,
            files=[discord.File(rendered, filename="displayname.png")]
        )

        update_command_stats(interaction.user.id, 'displayname')


async def setup(client: commands.Bot) -> None:
    await client.add_cog(DisplayName(client))
