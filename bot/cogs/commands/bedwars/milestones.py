import asyncio
import sqlite3

import discord
from discord import app_commands
from discord.ext import commands

from render.milestones import render_milestones
from statalib import (
    fetch_player_info,
    username_autocompletion,
    session_autocompletion,
    generic_command_cooldown,
    fetch_hypixel_data,
    update_command_stats,
    fetch_skin_model,
    handle_modes_renders,
    loading_message,
    find_dynamic_session
)


class Milestones(commands.Cog):
    def __init__(self, client):
        self.client: commands.Bot = client
        self.LOADING_MSG = loading_message()


    @app_commands.command(
        name="milestones",
        description="View the milestone stats of a player")
    @app_commands.describe(
        player='The player you want to view',
        session='The session you want to use (0 for none)')
    @app_commands.autocomplete(
        player=username_autocompletion,
        session=session_autocompletion)
    @app_commands.checks.dynamic_cooldown(generic_command_cooldown)
    async def milestones(self, interaction: discord.Interaction,
                         player: str=None, session: int=None):
        await interaction.response.defer()
        name, uuid = await fetch_player_info(player, interaction)

        # check if session if valid only if a session is being used
        if session == 0:
            valid_session = 0
        else:
            valid_session = find_dynamic_session(uuid, session)

        # session is not specified and none are found, so use no session
        if session is None and valid_session is None:
            valid_session = 0
        # specified session doesnt exist
        elif valid_session is None:
            await interaction.followup.send(
                f"`{name}` doesn't have an active session with ID: `{session or 1}`!\n"
                "Select a valid session or specify `0` in order to not use a session!")
            return

        await interaction.followup.send(self.LOADING_MSG)

        skin_model, hypixel_data = await asyncio.gather(
            fetch_skin_model(uuid, 128),
            fetch_hypixel_data(uuid)
        )

        kwargs = {
            "name": name,
            "uuid": uuid,
            "session": valid_session,
            "hypixel_data": hypixel_data,
            "skin_model": skin_model,
            "save_dir": interaction.id
        }

        await handle_modes_renders(interaction, render_milestones, kwargs)
        update_command_stats(interaction.user.id, 'milestones')


async def setup(client: commands.Bot) -> None:
    await client.add_cog(Milestones(client))
