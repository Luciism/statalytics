import asyncio
from typing import final

import discord
import statalib as lib
from discord.ext import commands
from statalib import render2
from statalib.hypixel import rround
from typing_extensions import override

import helper
from calc.quests import QuestStats


def quests_completed_text(levels_gained: int, completed: int) -> list[render2.TSpan]:
    prestige = lib.render.Prestige(levels_gained)

    tspans = [
        render2.TSpan(value=char, fill=color.hex)
        for char, color in prestige.char_to_color_map()
    ]

    return [*tspans, render2.TSpan(value=f" ({completed:,} Done)", font_size="0.85em")]


@final
class QuestStatsRenderer(render2.RenderingClient):
    def __init__(
        self,
        skin_model_bytes: bytes,
        username: str,
        data: lib.HypixelData,
    ) -> None:
        super().__init__(route="quests")

        self._skin_model_bytes = skin_model_bytes
        self._username = username
        self._data = data

    @override
    def placeholder_values(self) -> render2.PlaceholderValues:
        stats = QuestStats(self._data)

        xp_progress = stats.leveling.progression

        prestige = lib.render.Prestige(int(stats.level))
        prestige_gradient = prestige.colors.seven_step_gradient

        text_placeholders = {
            "quest_first_win_of_the_day#text": quests_completed_text(
                stats.lvls_daily_win, stats.completions_daily_win
            ),
            "quest_bed_removal_co#text": quests_completed_text(
                stats.lvls_weekly_bed_elims, stats.completions_weekly_bed_elims
            ),
            "quest_one_more_game#text": quests_completed_text(
                stats.lvls_daily_one_more, stats.completions_daily_one_more
            ),
            "quest_sleep_tight#text": quests_completed_text(
                stats.lvls_weekly_dream_win, stats.completions_weekly_dream_win
            ),
            "quest_painsomnia#text": quests_completed_text(
                stats.lvls_daily_bed_breaker, stats.completions_daily_bed_breaker
            ),
            "quest_challenger#text": quests_completed_text(
                stats.lvls_weekly_challenges_win,
                stats.completions_weekly_challenges_win,
            ),
            "quest_head_hunter#text": quests_completed_text(
                stats.lvls_daily_final_killer, stats.completions_daily_final_killer
            ),
            "quest_finishing_the_job#text": quests_completed_text(
                stats.lvls_weekly_final_killer, stats.completions_weekly_final_killer
            ),
            "quests_completed#text": f"{stats.quests_completed:,}",
            "hours_per_star_without_quests#text": f"{rround(stats.questless_hours_per_star, 2)}",
            "hours_per_star_with_quests#text": f"{rround(stats.hours_per_star, 2)}",
            "estimated_playtime#text": stats.formatted_estimated_playtime,
        }

        placeholder_values = render2.PlaceholderValues.new(text=text_placeholders)

        placeholder_values.add_current_level(
            stats.stars - stats.stars_from_quests, "stars_without_quests"
        )
        placeholder_values.add_current_level(
            stats.stars_from_quests, "stars_from_quests"
        )

        placeholder_values.add_progress_bar(
            prestige_gradient, xp_progress.progress_percent
        )
        placeholder_values.add_skin_model(self._skin_model_bytes)
        placeholder_values.add_footer_text()
        placeholder_values.add_current_and_next_level(int(stats.level))
        placeholder_values.add_xp_progress_text(stats.leveling.progression)
        placeholder_values.add_playername(stats.get_rank_info(self._username))

        return placeholder_values


class QuestsCommandCog(commands.Cog):
    @helper.decorators.app_command("quests")
    @helper.interactions.access_permitted_check()
    async def quests(self, interaction: discord.Interaction, player: str | None = None):
        await interaction.response.defer()

        name, uuid = await helper.interactions.fetch_player_info(player, interaction)

        skin_model, hypixel_data = await asyncio.gather(
            lib.network.fetch_skin_model(uuid),
            lib.network.fetch_hypixel_data(uuid),
        )

        renderer = QuestStatsRenderer(skin_model, name, hypixel_data)
        background_img = renderer.bg(interaction.user.id, "quests", uuid)
        img_bytes = await renderer.render_to_buffer(background_img)
        
        await interaction.followup.send(
            content=helper.random_tip_message(interaction.user.id),
            files=[discord.File(img_bytes, filename="quests.png")],
        )


async def setup(client: helper.Client) -> None:
    await client.add_cog(QuestsCommandCog())
