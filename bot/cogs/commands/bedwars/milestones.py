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
    loading_message
)


class Milestones(commands.Cog):
    def __init__(self, client):
        self.client: discord.Client = client
        self.LOADING_MSG = loading_message()


    @app_commands.command(
        name="milestones",
        description="View the milestone stats of a player")
    @app_commands.describe(
        player='The player you want to view',
        session='The session you want to use (0 for none, defaults to 1 if active)')
    @app_commands.autocomplete(
        player=username_autocompletion,
        session=session_autocompletion)
    @app_commands.checks.dynamic_cooldown(generic_command_cooldown)
    async def milestones(self, interaction: discord.Interaction,
                         player: str=None, session: int=None):
        await interaction.response.defer()
        name, uuid = await fetch_player_info(player, interaction)

        if session is None:
            session = 100

        with sqlite3.connect('./database/core.db') as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT * FROM sessions WHERE session=? AND uuid=?",
                (int(str(session)[0]), uuid)
            )

            if not cursor.fetchone() and not session in (0, 100):
                await interaction.followup.send(
                    f"`{name}` doesn't have an active session with ID: `{session}`!\n"
                    "Select a valid session or specify `0` in order to not use session data!")
                return

        await interaction.followup.send(self.LOADING_MSG)
        session = 1 if session == 100 else session

        hypixel_data = await fetch_hypixel_data(uuid)
        skin_res = await fetch_skin_model(uuid, 128)

        kwargs = {
            "name": name,
            "uuid": uuid,
            "session": session,
            "hypixel_data": hypixel_data,
            "skin_res": skin_res,
            "save_dir": interaction.id
        }

        await handle_modes_renders(interaction, render_milestones, kwargs)
        update_command_stats(interaction.user.id, 'milestones')


async def setup(client: commands.Bot) -> None:
    await client.add_cog(Milestones(client))
