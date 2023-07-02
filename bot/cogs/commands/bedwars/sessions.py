import os
import sqlite3

import discord
from discord import app_commands
from discord.ext import commands

from render.session import render_session
from helper.linking import fetch_player_info, get_linked_data
from helper.functions import (
    username_autocompletion,
    session_autocompletion,
    get_command_cooldown,
    get_hypixel_data,
    update_command_stats,
    get_subscription,
    start_session,
    get_smart_session,
    fetch_skin_model,
    send_generic_renders,
    loading_message
)


class ManageSession(discord.ui.View):
    def __init__(self, session: int, uuid: str, method: str) -> None:
        super().__init__(timeout=20)
        self.method = method
        self.session = session
        self.uuid = uuid


    async def on_timeout(self) -> None:
        for item in self.children:
            item.disabled = True
        await self.message.edit(view=self)


    @discord.ui.button(label="Confirm", style=discord.ButtonStyle.danger, custom_id="confirm")
    async def delete(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer()
        button.disabled = True
        await self.message.edit(view=self)

        with sqlite3.connect('./database/sessions.db') as conn:
            cursor = conn.cursor()

            if self.method == "delete":
                cursor.execute("DELETE FROM sessions WHERE session = ? AND uuid = ?", (self.session, self.uuid))
                message = f'Session `{self.session}` has been deleted successfully!'
            else:
                cursor.execute("DELETE FROM sessions WHERE session = ? AND uuid = ?", (self.session, self.uuid))

        if self.method != "delete":
            start_session(self.uuid, self.session)
            message = f'Session `{self.session}` has been reset successfully!'
        await interaction.followup.send(message, ephemeral=True)


class Sessions(commands.Cog):
    def __init__(self, client):
        self.client: discord.Client = client
        self.LOADING_MSG = loading_message()


    session_group = app_commands.Group(
        name='session', 
        description='View and manage active sessions'
    )


    @session_group.command(name="stats", description="View the session stats of a player")
    @app_commands.autocomplete(username=username_autocompletion, session=session_autocompletion)
    @app_commands.describe(username='The player you want to view', session='The session you want to view')
    @app_commands.checks.dynamic_cooldown(get_command_cooldown)
    async def session(self, interaction: discord.Interaction, username: str=None, session: int=100):
        await interaction.response.defer()
        name, uuid = await fetch_player_info(username, interaction)

        refined = name.replace('_', r'\_')
        session_data = await get_smart_session(interaction, session, refined, uuid)
        if not session_data:
            return
        if session == 100:
            session = session_data[0]

        await interaction.followup.send(self.LOADING_MSG)
        os.makedirs(f'./database/activerenders/{interaction.id}')
        hypixel_data = await get_hypixel_data(uuid)
        skin_res = await fetch_skin_model(uuid, 144)

        kwargs = {
            "name": name,
            "uuid": uuid,
            "session": session,
            "hypixel_data": hypixel_data,
            "skin_res": skin_res,
            "save_dir": interaction.id
        }

        await send_generic_renders(interaction, render_session, kwargs)
        update_command_stats(interaction.user.id, 'session')


    @session_group.command(name="start", description="Starts a new session")
    async def start_session(self, interaction: discord.Interaction):
        await interaction.response.defer()
        linked_data = get_linked_data(interaction.user.id)

        if linked_data:
            uuid = linked_data[1]

            with sqlite3.connect('./database/sessions.db') as conn:
                cursor = conn.cursor()
                cursor.execute(f"SELECT * FROM sessions WHERE uuid='{uuid}' ORDER BY session ASC")
                sessions = cursor.fetchall()

            subscription = get_subscription(interaction.user.id)

            if len(sessions) < 2 or subscription and len(sessions) < 5:
                for i, session in enumerate(sessions):
                    if session[0] != i + 1:
                        sessionid = i + 1
                        start_session(uuid, session=sessionid)
                        break
                else:
                    sessionid = len(sessions) + 1
                    start_session(uuid, session=sessionid)
                await interaction.followup.send(
                    f'A new session was successfully created! Session ID: `{sessionid}`')
            else:
                await interaction.followup.send(
                    'You already have the maximum sessions active for your plan! To remove a session use `/session end <id>`!')
        else:
            await interaction.followup.send(
                """You don't have an account linked! In order to link use `/link`!
                Otherwise `/session stats <player>` will start a session if one doesn't already exist!""".replace('   ', ''))

        update_command_stats(interaction.user.id, 'startsession')


    @session_group.command(name="end", description="Ends an active session")
    @app_commands.autocomplete(session=session_autocompletion)
    @app_commands.describe(session='The session you want to delete')
    async def end_session(self, interaction: discord.Interaction, session: int = None):
        if session is None:
            session = 1

        linked_data = get_linked_data(interaction.user.id)

        if linked_data:
            uuid = linked_data[1]

            with sqlite3.connect('./database/sessions.db') as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM sessions WHERE session=? AND uuid=?", (session, uuid))
                session_data = cursor.fetchone()

            if session_data:
                view = ManageSession(session, uuid, method="delete")
                await interaction.response.send_message(
                    f'Are you sure you want to delete session {session}?', view=view, ephemeral=True)
                view.message = await interaction.original_response()

            else:
                await interaction.response.send_message(
                    f"You don't have an active session with ID: `{session}`!")
        else:
            await interaction.response.send_message(
                "You don't have an account linked! In order to link use `/link`!")

        update_command_stats(interaction.user.id, 'endsession')


    @session_group.command(name="reset", description="Resets an active session")
    @app_commands.autocomplete(session=session_autocompletion)
    @app_commands.describe(session='The session you want to reset')
    async def reset_session(self, interaction: discord.Interaction, session: int = None):
        linked_data = get_linked_data(interaction.user.id)

        if linked_data:
            uuid = linked_data[1]

            if session is None:
                session = 1

            with sqlite3.connect('./database/sessions.db') as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM sessions WHERE session=? AND uuid=?", (session, uuid))
                session_data = cursor.fetchone()

            if session_data:
                view = ManageSession(session, uuid, method="reset")
                await interaction.response.send_message(
                    f'Are you sure you want to reset session {session}?', view=view, ephemeral=True)
                view.message = await interaction.original_response()

            else:
                await interaction.response.send_message(
                    f"You don't have an active session with ID: `{session}`!")
        else:
            await interaction.response.send_message(
                "You don't have an account linked! In order to link use `/link`!")
        
        update_command_stats(interaction.user.id, 'resetsession')


    @session_group.command(name="active", description="View all active sessions")
    async def active_sessions(self, interaction: discord.Interaction):
        await interaction.response.defer()
        linked_data = get_linked_data(interaction.user.id)

        if linked_data:
            uuid = linked_data[1]

            with sqlite3.connect('./database/sessions.db') as conn:
                cursor = conn.cursor()
                cursor.execute(f"SELECT * FROM sessions WHERE uuid='{uuid}'")
                sessions = cursor.fetchall()
            session_list = [str(session[0]) for session in sessions]

            if session_list:
                session_string = ", ".join(session_list)
                await interaction.followup.send(
                    f'Your active sessions: `{session_string}`')
            else:
                await interaction.followup.send(
                    "You don't have any sessions active! Use `/session start` to create one!")
        else:
            await interaction.followup.send(
                "You don't have an account linked! In order to link use `/link`!")

        update_command_stats(interaction.user.id, 'activesessions')


async def setup(client: commands.Bot) -> None:
    await client.add_cog(Sessions(client))
