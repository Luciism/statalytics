import asyncio
from datetime import datetime, timedelta, timezone
from typing import final

import discord
import statalib as lib
from discord import app_commands
from discord.ext import commands
from statalib import render2
from statalib import rotational_stats as rotational
from statalib.hypixel import rround
from typing_extensions import override

import helper
from calc.difference import DifferenceStats


def generate_ratio_text(before: float, after: float) -> list[render2.TSpan]:
    delta = after - before
    if delta >= 0:
        color = "{variable:colors.positive}"
        num_prefix = "+"
    else:
        color = "{variable:colors.negative}"
        num_prefix = ""

    return [
        render2.TSpan(value=f"{rround(before, 2)}", fill="{variable:colors.primary}"),
        render2.TSpan(value=" → ", fill="{variable:colors.text}"),
        render2.TSpan(value=f"{rround(after, 2)}", fill="{variable:colors.primary}"),
        render2.TSpan(
            value=f" {num_prefix}{rround(delta, 2)}", fill=color, font_size="0.8em"
        ),
    ]


@final
class StatDifferenceRenderer(render2.RenderingClient):
    def __init__(
        self,
        skin_model_bytes: bytes,
        username: str,
        player_uuid: str,
        data: lib.HypixelData,
        tracker: str,
        relative_date: str,
        mode: lib.Mode,
    ) -> None:
        super().__init__(route="stat-difference")

        self._skin_model_bytes = skin_model_bytes
        self._username = username
        self._player_uuid = player_uuid
        self._data = data
        self._tracker = tracker
        self._relative_date = relative_date
        self.mode = mode

    @override
    def placeholder_values(self) -> render2.PlaceholderValues:
        mode = self.mode or lib.ModesEnum.OVERALL.value
        stats = DifferenceStats(self._player_uuid, self._tracker, self._data, mode)

        xp_progress = stats.leveling.progression

        prestige = lib.render.Prestige(int(stats.level))
        prestige_gradient = prestige.colors.seven_step_gradient

        text_placeholders = {
            "stat_final_kills#text": f"{stats.final_kills_cum:,}",
            "stat_final_deaths#text": f"{stats.final_deaths_cum:,}",
            "stat_fkdr_diff#text": generate_ratio_text(stats.fkdr_old, stats.fkdr_new),
            "stat_wins#text": f"{stats.wins_cum:,}",
            "stat_losses#text": f"{stats.losses_cum:,}",
            "stat_wlr_diff#text": generate_ratio_text(stats.wlr_old, stats.wlr_new),
            "stat_beds_broken#text": f"{stats.beds_broken_cum:,}",
            "stat_beds_lost#text": f"{stats.beds_lost_cum:,}",
            "stat_bblr_diff#text": generate_ratio_text(stats.bblr_old, stats.bblr_new),
            "stat_kills#text": f"{stats.kills_cum:,}",
            "stat_deaths#text": f"{stats.deaths_cum:,}",
            "stat_kdr_diff#text": generate_ratio_text(stats.kdr_old, stats.kdr_new),
            "stat_stars_gained#text": stats.stars_gained,
            "stat_games_played#text": f"{stats.games_played_cum:,}",
            "stat_most_played#text": stats.most_played_cum,
            "gamemode#text": mode.name,
            "time_period#text": stats.rotation_type.name.title(),
            "period_key#text": stats.rotation_type.singular_name().title(),
            "period_value#text": self._relative_date,
        }

        placeholder_values = render2.PlaceholderValues.new(text=text_placeholders)
        placeholder_values.add_progress_bar(
            prestige_gradient, xp_progress.progress_percent
        )
        placeholder_values.add_skin_model(self._skin_model_bytes)
        placeholder_values.add_footer_text()
        placeholder_values.add_current_and_next_level(int(stats.level))
        placeholder_values.add_current_and_next_level(int(stats.level))
        placeholder_values.add_xp_progress_text(stats.leveling.progression)
        placeholder_values.add_playername(stats.get_rank_info(self._username))

        return placeholder_values


class DifferenceCommandCog(commands.Cog):
    difference_group: app_commands.Group = app_commands.Group(
        name="difference",
        description="View the stat difference of a player over a period of time",
        allowed_contexts=app_commands.AppCommandContext(
            guild=True, dm_channel=True, private_channel=True
        ),
        allowed_installs=app_commands.AppInstallationType(guild=True, user=True),
    )

    async def difference_command(
        self, interaction: discord.Interaction, player: str | None, tracker: str
    ) -> None:
        await interaction.response.defer()

        name, uuid = await helper.interactions.fetch_player_info(player, interaction)

        await interaction.followup.send(lib.config.loading_message())

        skin_model, hypixel_data = await asyncio.gather(
            lib.network.fetch_skin_model(uuid),
            lib.network.fetch_hypixel_data(uuid),
        )

        utc_offset = rotational.get_dynamic_reset_time(uuid).utc_offset
        manager = rotational.RotationalStatsManager(uuid)

        rotational_data = manager.get_rotational_data(
            rotational.RotationType.from_string(tracker)
        )

        if not rotational_data:
            manager.initialize_rotational_tracking(hypixel_data)

            _ = await interaction.edit_original_response(
                content=f"Historical stats for {lib.fmt.fname(name)} will now be tracked."
            )
            return

        now = datetime.now(timezone(timedelta(hours=utc_offset)))
        match tracker:
            case "daily" | "weekly":
            # case "weekly":
                formatted_date = now.strftime(f"%b {now.day}{lib.fmt.ordinal(now.day)}, %Y")
            case "monthly":
                formatted_date = now.strftime(f"%B %Y")
            case _:
                formatted_date = now.strftime(f"%Y")

        renderer = StatDifferenceRenderer(
            skin_model,
            name,
            uuid,
            hypixel_data,
            tracker,
            formatted_date,
            lib.ModesEnum.OVERALL.value,
        )
        background_img = render2.backgrounds.load_background_for_user(
            interaction.user.id, "stat-difference"
        )
        img_bytes = await renderer.render_to_buffer(background_img)

        await interaction.followup.send(
            files=[discord.File(img_bytes, filename="overall.png")],
            view=helper.views.FractylModesView(
                interaction_origin=interaction,
                modes=lib.ModesEnum.non_dream_modes(),
                background_img=background_img,
                placeholder="Overall",
                renderer=renderer,
            ),
        )

    @helper.decorators.app_command("difference_daily", group=difference_group)
    @helper.interactions.access_permitted_check()
    async def daily(self, interaction: discord.Interaction, player: str | None = None):
        await self.difference_command(interaction, player, "daily")

    @helper.decorators.app_command("difference_weekly", group=difference_group)
    @helper.interactions.access_permitted_check()
    async def weekly(self, interaction: discord.Interaction, player: str | None = None):
        await self.difference_command(interaction, player, "weekly")

    @helper.decorators.app_command("difference_monthly", group=difference_group)
    @helper.interactions.access_permitted_check()
    async def monthly(
        self, interaction: discord.Interaction, player: str | None = None
    ):
        await self.difference_command(interaction, player, "monthly")

    @helper.decorators.app_command("difference_yearly", group=difference_group)
    @helper.interactions.access_permitted_check()
    async def yearly(self, interaction: discord.Interaction, player: str | None = None):
        await self.difference_command(interaction, player, "yearly")


async def setup(client: helper.Client) -> None:
    await client.add_cog(DifferenceCommandCog())
