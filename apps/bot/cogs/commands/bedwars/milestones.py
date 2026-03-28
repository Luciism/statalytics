import asyncio
from typing import final
from statalib import render2
from typing_extensions import override

import discord
from discord.ext import commands

import helper
import statalib as lib
from statalib.sessions import BedwarsSession, SessionManager
from calc.milestones import MilestonesStats

def milestone_value(
    value1: int | float,
    value2: int | float,
    value2_suffix: str,
    text: str,
    current_value1: int | None=None
) -> list[render2.TSpan]:
    if value1 >= 0 and (not current_value1 or value1 >= current_value1):
        value1_str = f"{value1:,}"
    else:
        value1_str = "Never"

    return [
        render2.TSpan(value1_str, fill="{variable:colors.positive}"),
        render2.TSpan(f" {text} ", fill="{variable:colors.text}", font_size="0.8em"),
        render2.TSpan(f"{value2:,}{value2_suffix}", fill="{variable:colors.accent}"),
    ]

@final
class MilestoneStatsRenderer(render2.RenderingClient):
    def __init__(
        self,
        skin_model_bytes: bytes,
        username: str,
        data: lib.HypixelData,
        session: BedwarsSession | None,
        mode: lib.Mode
    ) -> None:
        super().__init__(route="milestones")

        self._skin_model_bytes = skin_model_bytes
        self._username = username
        self._data = data
        self._session = session
        self.mode = mode


    @override
    def placeholder_values(self) -> render2.PlaceholderValues:
        mode = self.mode or lib.ModesEnum.OVERALL.value
        stats = MilestonesStats(self._session, self._data, mode)

        xp_progress = stats.leveling.progression

        prestige = lib.render.Prestige(int(stats.level))
        prestige_gradient = prestige.colors.seven_step_gradient

        wins = stats.get_wins()
        finals = stats.get_finals()
        kills = stats.get_kills()
        beds = stats.get_beds()

        text_placeholders = {
            "stat_wins_until_wlr#text": milestone_value(wins.x_until_target_ratio, wins.target_ratio, " WLR", "Wins Until"),
            "stat_wins_at_wlr#text": milestone_value(wins.value_at_ratio, wins.target_ratio, " WLR", "Wins At", stats.wins),
            "stat_wins_until_wins#text": milestone_value(wins.x_until_target_value, wins.target_value, "", "Wins Until"),

            "stat_kills_until_kdr#text": milestone_value(kills.x_until_target_ratio, kills.target_ratio, " KDR", "Kills Until"),
            "stat_kills_at_kdr#text": milestone_value(kills.value_at_ratio, kills.target_ratio, " KDR", "Kills At", stats.kills),
            "stat_kills_until_kills#text": milestone_value(kills.x_until_target_value, kills.target_value, "", "Kills Until"),

            "stat_beds_until_bblr#text": milestone_value(beds.x_until_target_ratio, beds.target_ratio, " BBLR", "Beds Broken Until"),
            "stat_beds_at_bblr#text": milestone_value(beds.value_at_ratio, beds.target_ratio, " BBLR", "Beds Broken At", stats.beds_broken),
            "stat_beds_until_beds#text": milestone_value(beds.x_until_target_value, beds.target_value, "", "Beds Broken Until"),

            "stat_final_kills_until_fkdr#text": milestone_value(finals.x_until_target_ratio, finals.target_ratio, " FKDR", "Final Kills Until"),
            "stat_final_kills_at_fkdr#text": milestone_value(finals.value_at_ratio, finals.target_ratio, " FKDR", "Final Kills At", stats.final_kills),
            "stat_final_kills_until_final_kills#text": milestone_value(finals.x_until_target_value, finals.target_value, "", "Final Kills Until"),

            "gamemode#text": mode.name,
            "session_used#text": f"#{self._session.session_id}" if self._session else "None"
        }

        placeholder_values = render2.PlaceholderValues.new(text=text_placeholders)
        placeholder_values.add_progress_bar(prestige_gradient, xp_progress.progress_percent)
        placeholder_values.add_skin_model(self._skin_model_bytes)
        placeholder_values.add_footer_text()
        placeholder_values.add_current_and_next_level(int(stats.level))
        placeholder_values.add_next_level(stats.target_level, "next_prestige")
        placeholder_values.add_xp_progress_text(stats.leveling.progression)
        placeholder_values.add_playername(stats.get_rank_info(self._username))

        return placeholder_values


class MilestonesCommandCog(commands.Cog):
    @helper.decorators.app_command("milestones")
    @helper.interactions.access_permitted_check()
    async def milestones(
        self,
        interaction: discord.Interaction,
        player: str | None=None,
        session: int | None=None
    ) -> None:
        await interaction.response.defer()

        name, uuid = await helper.interactions.fetch_player_info(player, interaction)

        if session == 0:  # Use no session if `0` is specified.
            session_info = None
        else:
            session_info = SessionManager(uuid).get_session(session)

            # Specified session doesn't exist
            if session_info is None and session is not None:
                await interaction.followup.send(
                    f"`{name}` doesn't have an active session with ID: `{session or 1}`!\n" +
                    "Select a valid session or specify `0` in order to not use a session!")
                return

        skin_model, hypixel_data = await asyncio.gather(
            lib.network.fetch_skin_model(uuid),
            lib.network.fetch_hypixel_data(uuid)
        )

        renderer = MilestoneStatsRenderer(
            skin_model,
            name,
            hypixel_data,
            session_info,
            lib.ModesEnum.OVERALL.value
        )
        background_img = renderer.bg(interaction.user.id, "milestones", uuid)
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


async def setup(client: helper.Client) -> None:
    await client.add_cog(MilestonesCommandCog())
