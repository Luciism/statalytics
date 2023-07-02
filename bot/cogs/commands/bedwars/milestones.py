import os
import sqlite3

import discord
from discord import app_commands
from discord.ext import commands

from render.milestones import render_milestones
from helper.linking import fetch_player_info
from helper.functions import (
    username_autocompletion,
    session_autocompletion,
    get_command_cooldown,
    get_hypixel_data,
    update_command_stats,
    fetch_skin_model,
    send_generic_renders,
    loading_message
)


class Milestones(commands.Cog):
    def __init__(self, client):
        self.client: discord.Client = client
        self.LOADING_MSG = loading_message()


    @app_commands.command(name="milestones", description="View the milestone stats of a player")
    @app_commands.autocomplete(username=username_autocompletion, session=session_autocompletion)
    @app_commands.describe(username='The player you want to view', session='The session you want to use (0 for none, defaults to 1 if active)')
    @app_commands.checks.dynamic_cooldown(get_command_cooldown)
    async def milestones(self, interaction: discord.Interaction, username: str=None, session: int=None):
        await interaction.response.defer()
        name, uuid = await fetch_player_info(username, interaction)

        if session is None:
            session = 100

        with sqlite3.connect('./database/sessions.db') as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM sessions WHERE session=? AND uuid=?", (int(str(session)[0]), uuid))
            if not cursor.fetchone() and not session in (0, 100):
                await interaction.response.send_message(
                    f"`{username}` doesn't have an active session with ID: `{session}`!\nSelect a valid session or specify `0` in order to not use session data!")
                return

        await interaction.followup.send(self.LOADING_MSG)
        os.makedirs(f'./database/activerenders/{interaction.id}')
        session = 1 if session == 100 else session

        hypixel_data = await get_hypixel_data(uuid)
        skin_res = await fetch_skin_model(uuid, 128)

        kwargs = {
            "name": name,
            "uuid": uuid,
            "session": session,
            "hypixel_data": hypixel_data,
            "skin_res": skin_res,
            "save_dir": interaction.id
        }

        await send_generic_renders(interaction, render_milestones, kwargs)
        update_command_stats(interaction.user.id, 'milestones')


async def setup(client: commands.Bot) -> None:
    await client.add_cog(Milestones(client))
