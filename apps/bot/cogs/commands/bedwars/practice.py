import asyncio
from typing import final
from statalib import render2
from typing_extensions import override

import discord
from discord.ext import commands

import statalib as lib
import helper
from calc.practice import PracticeStats


@final
class PracticeStatsRenderer(render2.RenderingClient):
    def __init__(
        self,
        skin_model_bytes: bytes,
        username: str,
        data: lib.HypixelData,
    ) -> None:
        super().__init__(route="practice-stats")

        self._skin_model_bytes = skin_model_bytes
        self._username = username
        self._data = data


    @override
    def placeholder_values(self) -> render2.PlaceholderValues:
        stats = PracticeStats(self._data)

        xp_progress = stats.leveling.progression

        prestige = lib.render.Prestige(int(stats.level))
        prestige_gradient = prestige.colors.seven_step_gradient

        text_placeholders = {
            "stat_bridging_success#text": f"{stats.bridging_completed:,}",
            "stat_bridging_fails#text": f"{stats.bridging_failed:,}",
            "stat_bridging_ratio#text": f"{stats.bridging_ratio:,}",
            "stat_tnt_success#text": f"{stats.tnt_completed:,}",
            "stat_tnt_fails#text": f"{stats.tnt_failed:,}",
            "stat_tnt_ratio#text": f"{stats.tnt_ratio:,}",
            "stat_mlg_success#text": f"{stats.mlg_completed:,}",
            "stat_mlg_fails#text": f"{stats.mlg_failed:,}",
            "stat_mlg_ratio#text": f"{stats.mlg_ratio:,}",
            "stat_pearl_success#text": f"{stats.pearl_completed:,}",
            "stat_pearl_fails#text": f"{stats.pearl_failed:,}",
            "stat_pearl_ratio#text": f"{stats.pearl_ratio:,}",
            "stat_straight_short_pb#text": stats.straight_short_record,
            "stat_straight_medium_pb#text": stats.straight_medium_record,
            "stat_straight_long_pb#text": stats.straight_long_record,
            "stat_diagonal_short_pb#text": stats.diagonal_short_record,
            "stat_diagonal_medium_pb#text": stats.diagonal_medium_record,
            "stat_diagonal_long_pb#text": stats.diagonal_long_record,

            "success_rate#text": f"{stats.success_rate}%",
            "total_attempts#text": f"{stats.total_attempts:,}",
            "blocks_placed#text": f"{stats.blocks_placed:,}",
            "straight_avg_speed#text": stats.straight_average_time,
            "diagonal_avg_speed#text": stats.diagonal_average_time,
        }

        placeholder_values = render2.PlaceholderValues.new(text=text_placeholders)
        placeholder_values.add_progress_bar(prestige_gradient, xp_progress.progress_percent)
        placeholder_values.add_skin_model(self._skin_model_bytes)
        placeholder_values.add_footer_text()
        placeholder_values.add_current_and_next_level(int(stats.level))
        placeholder_values.add_xp_progress_text(stats.leveling.progression)
        placeholder_values.add_playername(stats.get_rank_info(self._username))

        return placeholder_values


class PracticeCommandCog(commands.Cog):
    @helper.decorators.app_command("practice")
    @helper.interactions.access_permitted_check()
    async def practice(self, interaction: discord.Interaction, player: str | None=None):
        await interaction.response.defer()

        name, uuid = await helper.interactions.fetch_player_info(player, interaction)

        skin_model, hypixel_data = await asyncio.gather(
            lib.network.fetch_skin_model(uuid),
            lib.network.fetch_hypixel_data(uuid)
        )

        renderer = PracticeStatsRenderer(skin_model, name, hypixel_data)

        background_img = render2.backgrounds.load_background_for_user(interaction.user.id, "practice-stats")
        img_bytes = await renderer.render_to_buffer(background_img)
        
        await interaction.followup.send(
            files=[discord.File(img_bytes, filename="practice.png")],
        )


async def setup(client: helper.Client) -> None:
    await client.add_cog(PracticeCommandCog())
