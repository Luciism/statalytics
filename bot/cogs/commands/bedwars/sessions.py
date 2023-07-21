import sqlite3

import discord
from discord import app_commands
from discord.ext import commands

from render.session import render_session
from statalib import (
    FetchPlayer,
    fetch_player_info,
    get_linked_player,
    username_autocompletion,
    session_autocompletion,
    generic_command_cooldown,
    fetch_hypixel_data,
    update_command_stats,
    get_subscription,
    start_session,
    find_dynamic_session,
    fetch_skin_model,
    handle_modes_renders,
    loading_message,
    STATIC_CONFIG
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

        with sqlite3.connect('./database/core.db') as conn:
            cursor = conn.cursor()

            cursor.execute(
                "DELETE FROM sessions WHERE session = ? AND uuid = ?",
                (self.session, self.uuid)
            )

        if self.method == "reset":
            await start_session(self.uuid, self.session)
            await interaction.followup.send(
                f'Session `{self.session}` has been reset successfully!', ephemeral=True)
            return

        await interaction.followup.send(
            f'Session `{self.session}` has been deleted successfully!', ephemeral=True)


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
    @app_commands.checks.dynamic_cooldown(generic_command_cooldown)
    async def session(self, interaction: discord.Interaction, username: str=None, session: int=None):
        await interaction.response.defer()
        name, uuid = await fetch_player_info(username, interaction)

        session = await find_dynamic_session(interaction, name, uuid, session)

        await interaction.followup.send(self.LOADING_MSG)
        hypixel_data = await fetch_hypixel_data(uuid)
        skin_res = await fetch_skin_model(uuid, 144)

        kwargs = {
            "name": name,
            "uuid": uuid,
            "session": session,
            "hypixel_data": hypixel_data,
            "skin_res": skin_res,
            "save_dir": interaction.id
        }

        await handle_modes_renders(interaction, render_session, kwargs)
        update_command_stats(interaction.user.id, 'session')


    @session_group.command(name="start", description="Starts a new session")
    async def session_start(self, interaction: discord.Interaction):
        await interaction.response.defer()
        uuid = get_linked_player(interaction.user.id)

        if not uuid:
            await interaction.followup.send(
                "You don't have an account linked! In order to link use `/link`!\n"
                "Use `/session stats <player>` to create a session if none exists!")
            return

        with sqlite3.connect('./database/core.db') as conn:
            cursor = conn.cursor()
            cursor.execute(f"SELECT session FROM sessions WHERE uuid='{uuid}' ORDER BY session ASC")
            session_data = cursor.fetchall()

        subscription = get_subscription(interaction.user.id)
        sessions = len(session_data)

        if subscription:
            max_sessions = STATIC_CONFIG.get('max_premium_sessions', 5)
        else:
            max_sessions = STATIC_CONFIG.get('max_free_sessions', 2)

        if sessions > max_sessions:
            await interaction.followup.send(
                'You already have the maximum sessions active for your plan! '
                'To remove a session use `/session end <id>`!')
            return

        # Find the first gap in the active sessions
        for i, session in enumerate(session_data):
            if session[0] != i + 1:
                session_id = i + 1
                break
        else:
            session_id = sessions + 1

        await start_session(uuid, session=session_id)
        await interaction.followup.send(
            f'A new session was successfully created! Session ID: `{session_id}`')

        update_command_stats(interaction.user.id, 'startsession')


    @session_group.command(name="end", description="Ends an active session")
    @app_commands.autocomplete(session=session_autocompletion)
    @app_commands.describe(session='The session you want to delete')
    async def end_session(self, interaction: discord.Interaction, session: int = None):
        if session is None:
            session = 1

        uuid = get_linked_player(interaction.user.id)

        if not uuid:
            await interaction.response.send_message(
                "You don't have an account linked! In order to link use `/link`!")
            return

        with sqlite3.connect('./database/core.db') as conn:
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

        update_command_stats(interaction.user.id, 'endsession')


    @session_group.command(name="reset", description="Resets an active session")
    @app_commands.autocomplete(session=session_autocompletion)
    @app_commands.describe(session='The session you want to reset')
    async def reset_session(self, interaction: discord.Interaction, session: int = None):
        uuid = get_linked_player(interaction.user.id)

        if not uuid:
            await interaction.response.send_message(
                "You don't have an account linked! In order to link use `/link`!")
            return

        name = FetchPlayer(uuid=uuid).name
        session = await find_dynamic_session(interaction, name, uuid, session, eph=True)

        view = ManageSession(session, uuid, method="reset")
        await interaction.response.send_message(
            f'Are you sure you want to reset session {session}?', view=view, ephemeral=True)
        view.message = await interaction.original_response()


        update_command_stats(interaction.user.id, 'resetsession')


    @session_group.command(name="active", description="View all active sessions")
    async def active_sessions(self, interaction: discord.Interaction):
        await interaction.response.defer()
        uuid = get_linked_player(interaction.user.id)

        if not uuid:
            await interaction.followup.send(
                "You don't have an account linked! In order to link use `/link`!")
            return

        with sqlite3.connect('./database/core.db') as conn:
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

        update_command_stats(interaction.user.id, 'activesessions')


async def setup(client: commands.Bot) -> None:
    await client.add_cog(Sessions(client))
