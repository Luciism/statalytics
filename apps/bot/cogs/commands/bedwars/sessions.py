"""Code that needs to be rewritten"""

import asyncio

import discord
from discord import app_commands
from discord.ext import commands

import helper
import statalib as lib
from statalib.sessions import SessionManager
from render.session import render_session


class ManageSession(lib.shared_views.CustomBaseView):
    def __init__(self, session: int, uuid: str, action: str) -> None:
        super().__init__(timeout=20)
        self.action = action
        self.session = session
        self.uuid = uuid


    async def on_timeout(self) -> None:
        for item in self.children:
            item.disabled = True

        try:
            await self.message.edit(view=self)
        except discord.errors.NotFound:
            pass


    @discord.ui.button(
        label="Confirm", style=discord.ButtonStyle.danger, custom_id="confirm")
    async def delete(
        self, interaction: discord.Interaction, button: discord.ui.Button
    ) -> None:
        await interaction.response.defer()
        await helper.interactions.run_interaction_checks(interaction)

        button.disabled = True
        await self.message.edit(view=self)

        session_manager = lib.SessionManager(self.uuid)
        session_manager.delete_session(self.session)

        if self.action == "reset":
            hypixel_data = await lib.fetch_hypixel_data(self.uuid)
            session_manager.create_session(self.session, hypixel_data)

            await interaction.followup.send(
                f'Session `{self.session}` has been reset successfully!', ephemeral=True)
            return

        await interaction.followup.send(
            f'Session `{self.session}` has been deleted successfully!', ephemeral=True)


class Sessions(commands.Cog):
    def __init__(self, client):
        self.client: commands.Bot = client
        self.LOADING_MSG = lib.loading_message()


    session_group = app_commands.Group(
        name='session',
        description='View and manage active sessions',
        allowed_contexts=app_commands.AppCommandContext(
            guild=True, dm_channel=True, private_channel=True),
        allowed_installs=app_commands.AppInstallationType(guild=True, user=True)
    )


    @session_group.command(
        name="stats",
        description="View the session stats of a player")
    @app_commands.describe(
        player='The player you want to view',
        session='The session you want to view')
    @app_commands.autocomplete(
        player=lib.username_autocompletion,
        session=lib.session_autocompletion)
    @app_commands.checks.dynamic_cooldown(helper.generic_command_cooldown)
    async def session(
        self,
        interaction: discord.Interaction,
        player: str=None,
        session: int=None
    ) -> None:
        await interaction.response.defer()
        await helper.interactions.run_interaction_checks(interaction)

        name, uuid = await helper.interactions.fetch_player_info(player, interaction)

        await interaction.followup.send(self.LOADING_MSG)

        skin_model, hypixel_data = await asyncio.gather(
            lib.fetch_skin_model(uuid, 144),
            lib.fetch_hypixel_data(uuid)
        )

        session_info = await helper.interactions.find_dynamic_session_interaction(
            interaction_callback=interaction.edit_original_response,
            username=name,
            uuid=uuid,
            hypixel_data=hypixel_data,
            session=session
        )

        kwargs = {
            "name": name,
            "uuid": uuid,
            "session_info": session_info,
            "hypixel_data": hypixel_data,
            "skin_model": skin_model,
            "save_dir": interaction.id
        }

        await helper.interactions.handle_modes_renders(interaction, render_session, kwargs)
        lib.update_command_stats(interaction.user.id, 'session')


    @session_group.command(name="start", description="Starts a new session")
    async def session_start(self, interaction: discord.Interaction):
        await interaction.response.defer()
        await helper.interactions.run_interaction_checks(interaction)

        uuid = lib.get_linked_player(interaction.user.id)

        if not uuid:
            await interaction.followup.send(
                "You don't have an account linked! In order to link use `/link`!\n"
                "Use `/session stats <player>` to create a session if none exists!")
            return

        session_manager = lib.SessionManager(uuid)
        active_sessions = session_manager.active_sessions()
        active_sessions_count = len(active_sessions)

        max_user_sessions = lib.SubscriptionManager(interaction.user.id)\
            .get_subscription()\
            .package_property("max_sessions", 2)

        if active_sessions_count >= max_user_sessions:
            await interaction.followup.send(
                'You already have the maximum sessions active for your plan! '
                'To remove a session use `/session end <id>`!')
            return

        # Find the first gap in the active sessions
        for i, session in enumerate(sorted(active_sessions), start=1):
            if session != i:
                session_id = i
                break
        else:
            session_id = active_sessions_count + 1

        hypixel_data = await lib.fetch_hypixel_data(uuid)
        session_manager.create_session(session_id, hypixel_data)

        await interaction.followup.send(
            f'A new session was successfully created! Session ID: `{session_id}`')

        lib.update_command_stats(interaction.user.id, 'startsession')


    @session_group.command(name="end", description="Ends an active session")
    @app_commands.autocomplete(session=lib.session_autocompletion)
    @app_commands.describe(session='The session you want to delete')
    async def end_session(self, interaction: discord.Interaction, session: int=1):
        await helper.interactions.run_interaction_checks(interaction)

        uuid = lib.get_linked_player(interaction.user.id)
        if not uuid:
            await interaction.response.send_message(
                "You don't have an account linked! In order to link use `/link`!")
            return

        session_manager = lib.SessionManager(uuid)
        active_sessions = session_manager.active_sessions()

        if session in active_sessions:
            view = ManageSession(session, uuid, action="delete")

            await interaction.response.send_message(
                f'Are you sure you want to delete session {session}?',
                view=view, ephemeral=True)
            view.message = await interaction.original_response()

        else:
            await interaction.response.send_message(
                f"You don't have an active session with ID: `{session}`!")

        lib.update_command_stats(interaction.user.id, 'endsession')


    @session_group.command(name="reset", description="Resets an active session")
    @app_commands.describe(session='The session you want to reset')
    @app_commands.autocomplete(session=lib.session_autocompletion)
    async def reset_session(
        self,
        interaction: discord.Interaction,
        session: int=None
    ) -> None:
        await helper.interactions.run_interaction_checks(interaction)

        uuid = lib.get_linked_player(interaction.user.id)
        if not uuid:
            await interaction.response.send_message(
                "You don't have an account linked! In order to link use `/link`!")
            return

        session_info = SessionManager(uuid).get_session(session)
        if session_info is None:
            await interaction.response.send_message(
                f"Couldn't find a session with ID: `{session or 1}`")
            return

        view = ManageSession(session_info.session_id, uuid, action="reset")
        await interaction.response.send_message(
            f'Are you sure you want to reset session {session_info.session_id}?',
            view=view, ephemeral=True)
        view.message = await interaction.original_response()

        lib.update_command_stats(interaction.user.id, 'resetsession')


    @session_group.command(name="active", description="View all active sessions")
    async def active_sessions(self, interaction: discord.Interaction):
        await interaction.response.defer()
        await helper.interactions.run_interaction_checks(interaction)

        uuid = lib.get_linked_player(interaction.user.id)

        if not uuid:
            await interaction.followup.send(
                "You don't have an account linked! In order to link use `/link`!")
            return

        session_manager = lib.SessionManager(uuid)
        active_sessions = session_manager.active_sessions()

        if active_sessions:
            session_string = ", ".join([str(item) for item in active_sessions])
            await interaction.followup.send(
                f'Your active sessions: `{session_string}`')
        else:
            await interaction.followup.send(
                "You don't have any sessions active! Use `/session start` to create one!")

        lib.update_command_stats(interaction.user.id, 'activesessions')


async def setup(client: commands.Bot) -> None:
    await client.add_cog(Sessions(client))
