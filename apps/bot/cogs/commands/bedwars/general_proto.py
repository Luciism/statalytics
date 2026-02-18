import asyncio
from typing import final
from typing_extensions import override

import discord
import statalib as lib
from statalib import render2
from discord.ext import commands

import helper


@final
class GeneralStatsRenderer(render2.RenderingClient):
    def __init__(
        self,
        route: str,
        skin_model_bytes: bytes,
        username: str,
        data: lib.HypixelData,
        mode: lib.Mode
    ) -> None:
        super().__init__(route)

        self._skin_model_bytes = skin_model_bytes
        self._username = username
        self._data = data
        self._mode = mode


    @override
    def placeholder_values(self) -> render2.PlaceholderValues:
        bw_stats = lib.hypixel.BedwarsStats(self._data, self._mode)

        xp_progress = bw_stats.leveling.progression

        prestige = lib.render.Prestige(int(bw_stats.level))
        prestige_gradient = prestige.colors.seven_step_gradient

        text_placeholders = {
            "stat_final_kills#text": f"{bw_stats.final_kills:,}",
            "stat_final_deaths#text": f"{bw_stats.final_kills:,}",
            "stat_fkdr#text": f"{bw_stats.fkdr:,}",
            "stat_wins#text": f"{bw_stats.wins:,}",
            "stat_losses#text": f"{bw_stats.losses:,}",
            "stat_wlr#text": f"{bw_stats.wlr:,}",
            "stat_beds_broken#text": f"{bw_stats.beds_broken:,}",
            "stat_beds_lost#text": f"{bw_stats.beds_lost:,}",
            "stat_bblr#text": f"{bw_stats.bblr:,}",
            "stat_kills#text": f"{bw_stats.kills:,}",
            "stat_deaths#text": f"{bw_stats.deaths:,}",
            "stat_kdr#text": f"{bw_stats.kdr:,}",
            "stat_games_played#text": f"{bw_stats.games_played:,}",
            "stat_most_played#text": f"{bw_stats.most_played}",
            "gamemode#text": f"{self._mode.name}",
            "bedwars_tokens#text": f"{bw_stats.coins:,}",
            "slumber_tickets#text": f"{bw_stats.slumber_tickets:,}",
        }

        placeholder_values = render2.PlaceholderValues.new(text=text_placeholders)
        placeholder_values.add_progress_bar(prestige_gradient, xp_progress.progress_percent)
        placeholder_values.add_skin_model(self._skin_model_bytes)
        placeholder_values.add_footer_text()
        placeholder_values.add_current_and_next_level(int(bw_stats.level))
        placeholder_values.add_current_and_next_level(int(bw_stats.level))
        placeholder_values.add_xp_progress_text(bw_stats.leveling.progression)
        placeholder_values.add_playername(bw_stats.rank_info(self._username))

        return placeholder_values



class GeneralBedwarsStatsCog(commands.Cog):
    @helper.decorators.app_command("bedwars_stats_proto")
    @helper.interactions.access_permitted_check()
    async def bedwars_stats_proto(
        self, interaction: discord.Interaction, player: str | None = None
    ):
        await interaction.response.defer()

        name, uuid = await helper.interactions.fetch_player_info(player, interaction)

        skin_model, hypixel_data = await asyncio.gather(
            lib.network.fetch_skin_model(uuid, 320),
            lib.network.fetch_hypixel_data(uuid),
        )

        renderer = GeneralStatsRenderer("bedwars", skin_model, name, hypixel_data, lib.ModesEnum.OVERALL.value)
        background_img = render2.backgrounds.load_background_for_user(interaction.user.id, "total")

        img_bytes = await renderer.render_to_buffer(background_img)

        await interaction.followup.send(
            files=[discord.File(img_bytes, filename="general.png")]
        )


async def setup(client: helper.Client) -> None:
    await client.add_cog(GeneralBedwarsStatsCog())
