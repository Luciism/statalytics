import discord
from discord import app_commands
from discord.ext import commands

import statalib as lib
import helper
from render.compare import render_compare


class Compare(commands.Cog):
    def __init__(self, client):
        self.client: commands.Bot = client
        self.LOADING_MSG = lib.loading_message()


    @app_commands.command(
        name="compare",
        description="Compare a player's stats to another player's stats")
    @app_commands.describe(
        player_1='The primary player in the comparison',
        player_2='The secondary player in the comparison')
    @app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
    @app_commands.allowed_installs(guilds=True, users=True)
    @app_commands.autocomplete(
        player_1=lib.username_autocompletion,
        player_2=lib.username_autocompletion)
    @app_commands.checks.dynamic_cooldown(helper.generic_command_cooldown)
    async def compare(self, interaction: discord.Interaction,
                      player_1: str, player_2: str=None):
        await interaction.response.defer()
        await helper.interactions.run_interaction_checks(interaction)

        name_1 = player_1 if player_2 else None
        name_2 = player_2 if player_2 else player_1

        name_1, uuid_1 = await helper.interactions.fetch_player_info(name_1, interaction)
        name_2, uuid_2 = await helper.interactions.fetch_player_info(name_2, interaction)

        await interaction.followup.send(self.LOADING_MSG)
        hypixel_data_1 = await lib.fetch_hypixel_data(uuid_1)
        hypixel_data_2 = await lib.fetch_hypixel_data(uuid_2)

        kwargs = {
            "name_1": name_1,
            "name_2": name_2,
            "uuid_1": uuid_1,
            "hypixel_data_1": hypixel_data_1,
            "hypixel_data_2": hypixel_data_2,
            "save_dir": interaction.id
        }

        await helper.interactions.handle_modes_renders(interaction, render_compare, kwargs)
        lib.update_command_stats(interaction.user.id, 'compare')


async def setup(client: commands.Bot) -> None:
    await client.add_cog(Compare(client))
