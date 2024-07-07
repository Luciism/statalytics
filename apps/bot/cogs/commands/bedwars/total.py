import asyncio
from typing import Callable

import discord
from discord import app_commands
from discord.ext import commands

import statalib as lib
from render.total import render_total
from render.pointless import render_pointless


class Total(commands.Cog):
    def __init__(self, client):
        self.client: commands.Bot = client
        self.LOADING_MSG = lib.loading_message()


    async def total_command(
        self, interaction: discord.Interaction,
        player: str, method: str, render_func: Callable
    ):
        await interaction.response.defer()
        await lib.run_interaction_checks(interaction)

        name, uuid = await lib.fetch_player_info(player, interaction)

        await interaction.followup.send(self.LOADING_MSG)

        skin_model, hypixel_data = await asyncio.gather(
            lib.fetch_skin_model(uuid, 144),
            lib.fetch_hypixel_data(uuid)
        )

        kwargs = {
            "name": name,
            "uuid": uuid,
            "hypixel_data": hypixel_data,
            "skin_model": skin_model,
            "save_dir": interaction.id
        }

        await lib.handle_modes_renders(interaction, render_func, kwargs)
        lib.update_command_stats(interaction.user.id, method)


    @app_commands.command(
        name="bedwars",
        description="View the general stats of a player")
    @app_commands.describe(player='The player you want to view')
    @app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
    @app_commands.allowed_installs(guilds=True, users=True)
    @app_commands.autocomplete(player=lib.username_autocompletion)
    @app_commands.checks.dynamic_cooldown(lib.generic_command_cooldown)
    async def total(self, interaction: discord.Interaction, player: str=None):
        await self.total_command(
            interaction, player, method='generic', render_func=render_total)


    @app_commands.command(
        name="pointless",
        description="View the general pointless stats of a player")
    @app_commands.describe(player='The player you want to view')
    @app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
    @app_commands.allowed_installs(guilds=True, users=True)
    @app_commands.autocomplete(player=lib.username_autocompletion)
    @app_commands.checks.dynamic_cooldown(lib.generic_command_cooldown)
    async def pointless(self, interaction: discord.Interaction,
                        player: str=None):
        await self.total_command(
            interaction, player, method='pointless', render_func=render_pointless)


async def setup(client: commands.Bot) -> None:
    await client.add_cog(Total(client))
