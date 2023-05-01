import os
import sqlite3

import discord
from discord import app_commands
from discord.ext import commands

from ui import SelectView
from render.rendermilestones import rendermilestones
from functions import (username_autocompletion,
                       session_autocompletion,
                       check_subscription,
                       get_hypixel_data,
                       update_command_stats,
                       authenticate_user)


class Milestones(commands.Cog):
    def __init__(self, client):
        self.client = client
        self.GENERATING_MESSAGE = 'Generating please wait <a:loading1:1062561739989860462>'

    # Milestone Stats
    @app_commands.command(name = "milestones", description = "View the milestone stats of a player")
    @app_commands.autocomplete(username=username_autocompletion, session=session_autocompletion)
    @app_commands.describe(username='The player you want to view', session='The session you want to use (0 for none, defaults to 1 if active)')
    @app_commands.checks.dynamic_cooldown(check_subscription)
    async def milestones(self, interaction: discord.Interaction, username: str=None, session: int=None):
        try: name, uuid = await authenticate_user(username, interaction)
        except TypeError: return

        if session is None: session = 100
        with sqlite3.connect('./database/sessions.db') as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM sessions WHERE session=? AND uuid=?", (int(str(session)[0]), uuid))
            if not cursor.fetchone() and not session in (0, 100):
                await interaction.response.send_message(f"`{username}` doesn't have an active session with ID: `{session}`!\nSelect a valid session or specify `0` in order to not use session data!")
                return

        await interaction.response.send_message(self.GENERATING_MESSAGE)
        os.makedirs(f'./database/activerenders/{interaction.id}')
        session = 1 if session == 100 else session
        hypixel_data = get_hypixel_data(uuid)

        rendermilestones(name, uuid, mode="Overall", session=session, hypixel_data=hypixel_data, save_dir=interaction.id)
        view = SelectView(user=interaction.user.id, inter=interaction, mode='Select a mode')
        await interaction.edit_original_response(content=None, attachments=[discord.File(f"./database/activerenders/{interaction.id}/overall.png")], view=view)
        rendermilestones(name, uuid, mode="Solos", session=session, hypixel_data=hypixel_data, save_dir=interaction.id)
        rendermilestones(name, uuid, mode="Doubles", session=session, hypixel_data=hypixel_data, save_dir=interaction.id)
        rendermilestones(name, uuid, mode="Threes", session=session, hypixel_data=hypixel_data, save_dir=interaction.id)
        rendermilestones(name, uuid, mode="Fours", session=session, hypixel_data=hypixel_data, save_dir=interaction.id)

        update_command_stats(interaction.user.id, 'milestones')

async def setup(client: commands.Bot) -> None:
    await client.add_cog(Milestones(client))
