import asyncio
from datetime import UTC, datetime
from typing import final
from statalib import render2
from statalib.color import ColorString
from statalib.hypixel import add_suffixes
from statalib.sessions import BedwarsSession
from typing_extensions import override

import discord
import statalib as lib
from discord import app_commands
from discord.ext import commands
from statalib.accounts import Account

from calc.year import YearStats
import helper

@final
class ProjectedStatsRenderer(render2.RenderingClient):
    def __init__(
        self,
        skin_model_bytes: bytes,
        username: str,
        player_uuid: str,
        target_year: int,
        data: lib.HypixelData,
        session: BedwarsSession,
        mode: lib.Mode
    ) -> None:
        super().__init__(route="projected-stats-at-year")

        self._skin_model_bytes = skin_model_bytes
        self._username = username
        self._player_uuid = player_uuid
        self._target_year = target_year
        self._data = data
        self._session = session
        self.mode = mode


    @override
    def placeholder_values(self) -> render2.PlaceholderValues:
        mode = self.mode or lib.ModesEnum.OVERALL.value
        stats = YearStats(self._player_uuid, self._session, self._target_year, self._data, mode)

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
            "stat_stars_per_day#text": add_suffixes(stats.levels_per_day),

            "gamemode#text": mode.name,
            "target_year#text": str(self._target_year),
            "days_to_go#text": f"{stats.days_to_go:,}",
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
        placeholder_values.add_next_level(int(stats.target_level), "level_next")
        placeholder_values.add_playername(stats.get_rank_info(self._username))

        return placeholder_values


class YearCommandCog(commands.Cog):
    year_group: app_commands.Group = app_commands.Group(
        name="year",
        description="View the a players projected stats for a future year",
        allowed_contexts=app_commands.AppCommandContext(
            guild=True, dm_channel=True, private_channel=True
        ),
        allowed_installs=app_commands.AppInstallationType(guild=True, user=True),
    )

    async def year_command(
        self,
        interaction: discord.Interaction,
        name: str,
        uuid: str,
        session: int | None,
        year: int,
    ) -> None:
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

        renderer = ProjectedStatsRenderer(
            skin_model,
            name,
            uuid,
            year,
            hypixel_data,
            session_info,
            lib.ModesEnum.OVERALL.value
        )
        background_img = renderer.bg(interaction.user.id, "year_projection", uuid)
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



    YEAR1: int = datetime.now(UTC).year + 1
    YEAR2: int = datetime.now(UTC).year + 2

    @helper.decorators.app_command(f"year_{YEAR1}", group=year_group)
    @helper.interactions.access_permitted_check()
    async def year_1(
        self,
        interaction: discord.Interaction,
        player: str | None = None,
        session: int | None = None,
    ) -> None:
        await interaction.response.defer()
        name, uuid = await helper.interactions.fetch_player_info(player, interaction)
        await self.year_command(interaction, name, uuid, session, self.YEAR1)

    @helper.decorators.app_command(f"year_{YEAR2}", group=year_group)
    @helper.interactions.access_permitted_check()
    async def year_2(
        self,
        interaction: discord.Interaction,
        player: str | None = None,
        session: int | None = None,
    ) -> None:
        await interaction.response.defer()
        name, uuid = await helper.interactions.fetch_player_info(player, interaction)

        discord_id = lib.accounts.uuid_to_discord_id(uuid)

        # Either command user or checked player has access
        condition_1 = False
        if discord_id is not None:
            condition_1 = Account(discord_id).permissions.has_access(f"year_{self.YEAR2}")

        condition_2 = Account(interaction.user.id).permissions.has_access(
            f"year_{self.YEAR2}"
        )

        if not condition_1 and not condition_2:
            embed = helper.Embeds.problems.no_premium__year_projection()
            await interaction.followup.send(embed=embed)
            return

        await self.year_command(interaction, name, uuid, session, self.YEAR2)


async def setup(client: helper.Client) -> None:
    await client.add_cog(YearCommandCog())
