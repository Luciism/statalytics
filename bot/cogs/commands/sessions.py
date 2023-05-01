import os
import sqlite3

import discord
from discord import app_commands
from discord.ext import commands

from functions import (username_autocompletion,
                       session_autocompletion,
                       check_subscription,
                       get_hypixel_data,
                       update_command_stats,
                       get_linked_data,
                       get_subscription,
                       start_session,
                       authenticate_user,
                       skin_session)

from render.rendersession import rendersession
from ui import SelectView, ManageSession

class Sessions(commands.Cog):
    def __init__(self, client):
        self.client = client
        self.GENERATING_MESSAGE = 'Generating please wait <a:loading1:1062561739989860462>'

    # View Session Command
    @app_commands.command(name = "session", description = "View the session stats of a player")
    @app_commands.autocomplete(username=username_autocompletion, session=session_autocompletion)
    @app_commands.describe(username='The player you want to view', session='The session you want to view')
    @app_commands.checks.dynamic_cooldown(check_subscription)
    async def session(self, interaction: discord.Interaction, username: str=None, session: int=None):
        try: name, uuid = await authenticate_user(username, interaction)
        except TypeError: return

        if session is None: session = 100

        refined = name.replace('_', r'\_')
        with sqlite3.connect('./database/sessions.db') as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM sessions WHERE session=? AND uuid=?", (int(str(session)[0]), uuid))
            session_data = cursor.fetchone()
            if not session_data:
                cursor.execute(f"SELECT * FROM sessions WHERE uuid='{uuid}' ORDER BY session ASC")
                session_data = cursor.fetchone()

        if not session_data:
            await interaction.response.defer()
            response = start_session(uuid, session=1)

            if response is True: await interaction.followup.send(f"**{refined}** has no active sessions so one was created!")
            else: await interaction.followup.send(f"**{refined}** has never played before!")
            return
        elif session_data[0] != session and session != 100: 
            await interaction.response.send_message(f"**{refined}** doesn't have an active session with ID: `{session}`!")
            return

        if session == 100: session = session_data[0]
        await interaction.response.send_message(self.GENERATING_MESSAGE)
        os.makedirs(f'./database/activerenders/{interaction.id}')
        hypixel_data = get_hypixel_data(uuid)
        skin_res = skin_session.get(f'https://visage.surgeplay.com/bust/144/{uuid}', timeout=10)

        rendersession(name, uuid, session, mode="Overall", hypixel_data=hypixel_data, skin_res=skin_res.content, save_dir=interaction.id)
        view = SelectView(user=interaction.user.id, inter=interaction, mode='Select a mode')
        await interaction.edit_original_response(content=None, attachments=[discord.File(f"./database/activerenders/{interaction.id}/overall.png")], view=view)
        rendersession(name, uuid, session, mode="Solos", hypixel_data=hypixel_data, skin_res=skin_res.content, save_dir=interaction.id)
        rendersession(name, uuid, session, mode="Doubles", hypixel_data=hypixel_data, skin_res=skin_res.content, save_dir=interaction.id)
        rendersession(name, uuid, session, mode="Threes", hypixel_data=hypixel_data, skin_res=skin_res.content, save_dir=interaction.id)
        rendersession(name, uuid, session, mode="Fours", hypixel_data=hypixel_data, skin_res=skin_res.content, save_dir=interaction.id)

        update_command_stats(interaction.user.id, 'session')

    # Create Session Command
    @app_commands.command(name = "startsession", description = "Starts a new session")
    async def start_session(self, interaction: discord.Interaction):
        linked_data = get_linked_data(interaction.user.id)

        if linked_data:
            await interaction.response.defer()
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
                await interaction.followup.send(f'A new session was successfully created! Session ID: `{sessionid}`')
            else:
                await interaction.followup.send('You already have the maximum sessions active for your plan! To remove a session use `/endsession <id>`!')
        else:
            await interaction.response.send_message("""You don't have an account linked! In order to link use `/link`!
                                                    Otherwise use `/session <player>` will start a session if one doesn't already exist!""")


    # Delete Session Command
    @app_commands.command(name = "endsession", description = "Ends an active session")
    @app_commands.autocomplete(session=session_autocompletion)
    @app_commands.describe(session='The session you want to delete')
    async def end_session(self, interaction: discord.Interaction, session: int = None):
        if session is None: session = 1

        linked_data = get_linked_data(interaction.user.id)

        if linked_data:
            uuid = linked_data[1]

            with sqlite3.connect('./database/sessions.db') as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM sessions WHERE session=? AND uuid=?", (session, uuid))
                session_data = cursor.fetchone()
            if session_data:
                view = ManageSession(session, uuid, method="delete")
                await interaction.response.send_message(f'Are you sure you want to delete session {session}?', view=view, ephemeral=True)
                view.message = await interaction.original_response()
            else:
                await interaction.response.send_message(f"You don't have an active session with ID: `{session}`!")
        else:
            await interaction.response.send_message("You don't have an account linked! In order to link use `/link`!")


    # Reset Session Command
    @app_commands.command(name = "resetsession", description = "Resets an active session")
    @app_commands.autocomplete(session=session_autocompletion)
    @app_commands.describe(session='The session you want to reset')
    async def reset_session(self, interaction: discord.Interaction, session: int = None):
        linked_data = get_linked_data(interaction.user.id)

        if linked_data:
            uuid = linked_data[1]

            if session is None: session = 1

            with sqlite3.connect('./database/sessions.db') as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM sessions WHERE session=? AND uuid=?", (session, uuid))
                session_data = cursor.fetchone()

            if session_data:
                view = ManageSession(session, uuid, method="reset")
                await interaction.response.send_message(f'Are you sure you want to reset session {session}?', view=view, ephemeral=True)
                view.message = await interaction.original_response()
            else:
                await interaction.response.send_message(f"You don't have an active session with ID: `{session}`!")
        else:
            await interaction.response.send_message("You don't have an account linked! In order to link use `/link`!")


    # Session List Command
    @app_commands.command(name = "activesessions", description = "View all active sessions")
    async def active_sessions(self, interaction: discord.Interaction):
        linked_data = get_linked_data(interaction.user.id)

        if linked_data:
            await interaction.response.defer()
            uuid = linked_data[1]

            with sqlite3.connect('./database/sessions.db') as conn:
                cursor = conn.cursor()
                cursor.execute(f"SELECT * FROM sessions WHERE uuid='{uuid}'")
                sessions = cursor.fetchall()
            session_list = [str(session[0]) for session in sessions]

            if session_list:
                session_string = ", ".join(session_list)
                await interaction.followup.send(f'Your active sessions: `{session_string}`')
            else:
                await interaction.followup.send("You don't have any sessions active! Use `/startsession` to create one!")
        else:
            await interaction.response.send_message("You don't have an account linked! In order to link use `/link`!")

async def setup(client: commands.Bot) -> None:
    await client.add_cog(Sessions(client))
