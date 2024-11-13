import discord
from discord import app_commands
from discord.ext import commands

import statalib as lib
import helper
from render.resources import render_resources


class Resources(commands.Cog):
    def __init__(self, client):
        self.client: commands.Bot = client
        self.LOADING_MSG = lib.loading_message()


    @app_commands.command(
        name="resources",
        description="View the resource stats of a player")
    @app_commands.describe(player='The player you want to view')
    @app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
    @app_commands.allowed_installs(guilds=True, users=True)
    @app_commands.autocomplete(player=lib.username_autocompletion)
    @app_commands.checks.dynamic_cooldown(helper.generic_command_cooldown)
    async def resources(self, interaction: discord.Interaction,
                        player: str=None):
        await interaction.response.defer()
        await helper.interactions.run_interaction_checks(interaction)

        name, uuid = await helper.interactions.fetch_player_info(player, interaction)

        await interaction.followup.send(self.LOADING_MSG)
        hypixel_data = await lib.fetch_hypixel_data(uuid)

        kwargs = {
            "name": name,
            "uuid": uuid,
            "hypixel_data": hypixel_data,
            "save_dir": interaction.id
        }

        await helper.interactions.handle_modes_renders(interaction, render_resources, kwargs)
        lib.update_command_stats(interaction.user.id, 'resources')


async def setup(client: commands.Bot) -> None:
    await client.add_cog(Resources(client))
