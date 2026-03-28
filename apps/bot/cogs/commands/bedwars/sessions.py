"""Code that needs to be rewritten"""

import asyncio
from typing import Self, cast, final

import discord
import statalib as lib
from discord import app_commands
from discord.ext import commands
from statalib import render2
from statalib.accounts import Account
from statalib.sessions import BedwarsSession, SessionManager
from typing_extensions import override

from calc.session import SessionStats
import helper

@final
class SessionStatsRenderer(render2.RenderingClient):
    def __init__(
        self,
        skin_model_bytes: bytes,
        username: str,
        player_uuid: str,
        data: lib.HypixelData,
        session: BedwarsSession,
        mode: lib.Mode
    ) -> None:
        super().__init__(route="session-stats")

        self._skin_model_bytes = skin_model_bytes
        self._username = username
        self._player_uuid = player_uuid
        self._data = data
        self._session = session
        self.mode = mode


    @override
    def placeholder_values(self) -> render2.PlaceholderValues:
        mode = self.mode or lib.ModesEnum.OVERALL.value
        stats = SessionStats(self._player_uuid, self._session, self._data, mode)

        xp_progress = stats.leveling.progression

        prestige = lib.render.Prestige(int(stats.level))
        prestige_gradient = prestige.colors.seven_step_gradient

        text_placeholders = {
            "stat_wins#text": f"{stats.wins_cum:,}",
            "stat_losses#text": f"{stats.losses_cum:,}",
            "stat_wlr#text": f"{stats.wlr_cum:,}",

            "stat_final_kills#text": f"{stats.final_kills_cum:,}",
            "stat_final_deaths#text": f"{stats.final_deaths_cum:,}",
            "stat_fkdr#text": f"{stats.fkdr_cum:,}",

            "stat_kills#text": f"{stats.kills_cum:,}",
            "stat_deaths#text": f"{stats.deaths_cum:,}",
            "stat_kdr#text": f"{stats.kdr_cum:,}",

            "stat_beds_broken#text": f"{stats.beds_broken_cum:,}",
            "stat_beds_lost#text": f"{stats.beds_lost_cum:,}",
            "stat_bblr#text": f"{stats.bblr_cum:,}",

            "stat_wins_per_day#text": f"{stats.wins_per_day:,}",
            "stat_final_kills_per_day#text": f"{stats.final_kills_per_day:,}",
            "stat_stars_per_day#text": f"{stats.stars_gained_per_day:,}",

            "gamemode#text": mode.name,
            "session_id#text": f"#{self._session.session_id}",
            "session_date_started#text": stats.date_started,
            "games_played#text": f"{stats.games_played:,}",
            "stars_gained#text": f"{stats.stars_gained:,}",
        }


        placeholder_values = render2.PlaceholderValues.new(text=text_placeholders)
        placeholder_values.add_skin_model(self._skin_model_bytes)
        placeholder_values.add_footer_text()
        placeholder_values.add_progress_bar(prestige_gradient, xp_progress.progress_percent)
        placeholder_values.add_xp_progress_text(stats.leveling.progression)
        placeholder_values.add_current_and_next_level(int(stats.level))
        placeholder_values.add_playername(stats.get_rank_info(self._username))

        return placeholder_values


class ManageSession(helper.views.CustomBaseView):
    def __init__(self, session: int, uuid: str, action: str) -> None:
        super().__init__(timeout=20)
        self.action: str = action
        self.session: int = session
        self.uuid: str = uuid

        self.message: discord.InteractionMessage | None = None

    @override
    async def on_timeout(self) -> None:
        for item in self.children:
            if isinstance(item, (discord.ui.Button, discord.ui.Select)):
                item.disabled = True

        if self.message:
            try:
                _ = await self.message.edit(view=self)
            except discord.errors.NotFound:
                pass

    @discord.ui.button(
        label="Confirm", style=discord.ButtonStyle.danger, custom_id="confirm"
    )
    async def delete(
        self, interaction: discord.Interaction, button: discord.ui.Button[Self]
    ) -> None:
        await interaction.response.defer()
        await helper.interactions.run_interaction_checks(interaction)

        button.disabled = True
        if self.message:
            _ = await self.message.edit(view=self)

        session_manager = lib.sessions.SessionManager(self.uuid)

        try:
            session_manager.delete_session(self.session)
        except lib.errors.DataNotFoundError:
            pass

        if self.action == "reset":
            hypixel_data = await lib.network.fetch_hypixel_data(self.uuid)
            session_manager.create_session(self.session, hypixel_data)

            await interaction.followup.send(
                f"Session `{self.session}` has been reset successfully!", ephemeral=True
            )
            return

        await interaction.followup.send(
            f"Session `{self.session}` has been deleted successfully!", ephemeral=True
        )


class SessionsCommandCog(commands.Cog):
    session_group: app_commands.Group = app_commands.Group(
        name="session",
        description="View and manage active sessions",
        allowed_contexts=app_commands.AppCommandContext(
            guild=True, dm_channel=True, private_channel=True
        ),
        allowed_installs=app_commands.AppInstallationType(guild=True, user=True),
    )

    @helper.decorators.app_command("session_stats", group=session_group)
    @helper.interactions.access_permitted_check()
    async def session(
        self,
        interaction: discord.Interaction,
        player: str | None = None,
        session: int | None = None,
    ) -> None:
        await interaction.response.defer()

        name, uuid = await helper.interactions.fetch_player_info(player, interaction)

        skin_model, hypixel_data = await asyncio.gather(
            lib.network.fetch_skin_model(uuid),
            lib.network.fetch_hypixel_data(uuid),
        )

        session_info = await helper.interactions.find_dynamic_session_interaction(
            interaction_callback=interaction.edit_original_response,
            username=name,
            uuid=uuid,
            hypixel_data=hypixel_data,
            session=session,
        )

        renderer = SessionStatsRenderer(
            skin_model,
            name,
            uuid,
            hypixel_data,
            session_info,
            lib.ModesEnum.OVERALL.value
        )
        background_img = renderer.bg(interaction.user.id, "session", uuid)
        img_bytes = await renderer.render_to_buffer(background_img)
        
        await interaction.followup.send(
            files=[discord.File(img_bytes, filename="overall.png")],
            view=helper.views.FractylModesView(
                interaction_origin=interaction,
                modes=lib.ModesEnum.non_dream_modes(),
                background_img=background_img,
                placeholder="Overall",
                renderer=renderer
            )
        )

    @helper.decorators.app_command("session_start", group=session_group)
    @helper.interactions.access_permitted_check()
    async def session_start(self, interaction: discord.Interaction):
        await interaction.response.defer()

        uuid = Account(interaction.user.id).linking.get_linked_player_uuid()

        if not uuid:
            await interaction.followup.send(
                "You don't have an account linked! In order to link use `/link`!\n"
                + "Use `/session stats <player>` to create a session if none exists!"
            )
            return

        session_manager = lib.sessions.SessionManager(uuid)
        active_sessions = session_manager.active_sessions()
        active_sessions_count = len(active_sessions)

        max_user_sessions: int = cast(int, Account(interaction.user.id)
            .subscriptions.get_subscription()
            .package_property("max_sessions", 2)
        )

        if active_sessions_count >= max_user_sessions:
            await interaction.followup.send(
                "You already have the maximum sessions active for your plan! "
                + "To remove a session use `/session end <id>`!"
            )
            return

        # Find the first gap in the active sessions
        for i, session in enumerate(sorted(active_sessions), start=1):
            if session != i:
                session_id = i
                break
        else:
            session_id = active_sessions_count + 1

        hypixel_data = await lib.network.fetch_hypixel_data(uuid)
        session_manager.create_session(session_id, hypixel_data)

        await interaction.followup.send(
            f"A new session was successfully created! Session ID: `{session_id}`"
        )

    @helper.decorators.app_command("session_end", group=session_group)
    @helper.interactions.access_permitted_check()
    async def end_session(self, interaction: discord.Interaction, session: int = 1):
        uuid = Account(interaction.user.id).linking.get_linked_player_uuid()
        if not uuid:
            await interaction.response.send_message(
                "You don't have an account linked! In order to link use `/link`!"
            )
            return

        session_manager = lib.sessions.SessionManager(uuid)
        active_sessions = session_manager.active_sessions()

        if session in active_sessions:
            view = ManageSession(session, uuid, action="delete")

            await interaction.response.send_message(
                f"Are you sure you want to delete session {session}?",
                view=view,
                ephemeral=True,
            )
            view.message = await interaction.original_response()
        else:
            await interaction.response.send_message(
                f"You don't have an active session with ID: `{session}`!"
            )

    @helper.decorators.app_command("session_reset", group=session_group)
    @helper.interactions.access_permitted_check()
    async def reset_session(
        self, interaction: discord.Interaction, session: int | None = None
    ) -> None:
        uuid = Account(interaction.user.id).linking.get_linked_player_uuid()
        if not uuid:
            await interaction.response.send_message(
                "You don't have an account linked! In order to link use `/link`!"
            )
            return

        session_info = SessionManager(uuid).get_session(session)
        if session_info is None:
            await interaction.response.send_message(
                f"Couldn't find a session with ID: `{session or 1}`"
            )
            return

        view = ManageSession(session_info.session_id, uuid, action="reset")
        await interaction.response.send_message(
            f"Are you sure you want to reset session {session_info.session_id}?",
            view=view,
            ephemeral=True,
        )
        view.message = await interaction.original_response()

    @helper.decorators.app_command("session_list_active", group=session_group)
    @helper.interactions.access_permitted_check()
    async def active_sessions(self, interaction: discord.Interaction):
        await interaction.response.defer()

        uuid = Account(interaction.user.id).linking.get_linked_player_uuid()

        if not uuid:
            await interaction.followup.send(
                "You don't have an account linked! In order to link use `/link`!"
            )
            return

        session_manager = lib.sessions.SessionManager(uuid)
        active_sessions = session_manager.active_sessions()

        if active_sessions:
            session_string = ", ".join([str(item) for item in active_sessions])
            await interaction.followup.send(f"Your active sessions: `{session_string}`")
        else:
            await interaction.followup.send(
                "You don't have any sessions active! Use `/session start` to create one!"
            )


async def setup(client: helper.Client) -> None:
    await client.add_cog(SessionsCommandCog())
