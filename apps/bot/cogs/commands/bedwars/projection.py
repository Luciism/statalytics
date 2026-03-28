import asyncio
from typing import final
from statalib import render2
from statalib.color import ColorString
from statalib.sessions import BedwarsSession
from typing_extensions import override

import discord
from discord.ext import commands

import statalib as lib
from statalib.hypixel import BedwarsStats, add_suffixes
from calc.projection import PrestigeStats
import helper


@final
class ProjectedStatsRenderer(render2.RenderingClient):
    def __init__(
        self,
        skin_model_bytes: bytes,
        username: str,
        target_level: int,
        data: lib.HypixelData,
        session: BedwarsSession,
        mode: lib.Mode
    ) -> None:
        super().__init__(route="projected-stats-at-level")

        self._skin_model_bytes = skin_model_bytes
        self._username = username
        self._target_level = target_level
        self._data = data
        self._session = session
        self.mode = mode


    @override
    def placeholder_values(self) -> render2.PlaceholderValues:
        mode = self.mode or lib.ModesEnum.OVERALL.value
        stats = PrestigeStats(self._session, self._target_level, self._data, mode)

        text_placeholders = {
            "stat_wins#text": add_suffixes(stats.wins_projected),
            "stat_losses#text": add_suffixes(stats.losses_projected),
            "stat_wlr#text": add_suffixes(stats.wlr_projected),

            "stat_kills#text": add_suffixes(stats.kills_projected),
            "stat_deaths#text": add_suffixes(stats.deaths_projected),
            "stat_kdr#text": add_suffixes(stats.kdr_projected),

            "stat_beds_broken#text": add_suffixes(stats.beds_broken_projected),
            "stat_beds_lost#text": add_suffixes(stats.beds_lost_projected),
            "stat_bblr#text": add_suffixes(stats.bblr_projected),

            "stat_final_kills#text": add_suffixes(stats.final_kills_projected),
            "stat_final_deaths#text": add_suffixes(stats.final_deaths_projected),
            "stat_fkdr#text": add_suffixes(stats.fkdr_projected),

            "stat_wins_per_star#text": add_suffixes(stats.wins_per_star),
            "stat_final_kills_per_star#text": add_suffixes(stats.final_kills_per_star),
            "stat_beds_broken_per_star#text": add_suffixes(stats.beds_broken_per_star),

            "gamemode#text": mode.name,
            "projection_date#text": stats.projection_date,
            "xp_progress#text": f"{round(stats.complete_percentage)}% Complete",
        }

        shape_placeholders = {
            "progress_bar#width": f"{stats.complete_percentage}%",
            "progress_bar#fill": ColorString.GRAY.value.hex
        }

        placeholder_values = render2.PlaceholderValues.new(text=text_placeholders, shapes=shape_placeholders)
        placeholder_values.add_skin_model(self._skin_model_bytes)
        placeholder_values.add_footer_text()
        placeholder_values.add_current_level(int(stats.level))
        placeholder_values.add_next_level(int(stats.target), "target_level")
        placeholder_values.add_playername(stats.get_rank_info(self._username))

        return placeholder_values


class ProjectionCommandCog(commands.Cog):
    @helper.decorators.app_command("prestige")
    @helper.interactions.access_permitted_check()
    async def projected_stats(
        self,
        interaction: discord.Interaction,
        prestige: int | None=None,
        player: str | None=None,
        session: int | None=None
    ) -> None:
        await interaction.response.defer()

        name, uuid = await helper.interactions.fetch_player_info(player, interaction)

        skin_model, hypixel_data = await asyncio.gather(
            lib.network.fetch_skin_model(uuid),
            lib.network.fetch_hypixel_data(uuid)
        )

        session_info = await helper.interactions.find_dynamic_session_interaction(
            interaction_callback=interaction.edit_original_response,
            username=name,
            uuid=uuid,
            hypixel_data=hypixel_data,
            session=session
        )

        if not prestige:
            stats = BedwarsStats(hypixel_data, lib.ModesEnum.OVERALL.value)
            current_star = int(stats.level)
            target_level: int = (current_star // 100 + 1) * 100
        else:
            target_level = max(prestige, 1)

        renderer = ProjectedStatsRenderer(
            skin_model,
            name,
            target_level,
            hypixel_data,
            session_info,
            lib.ModesEnum.OVERALL.value
        )
        background_img = renderer.bg(interaction.user.id, "projection", uuid)
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
    await client.add_cog(ProjectionCommandCog())
