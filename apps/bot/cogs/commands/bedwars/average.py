import asyncio
from typing import final
from typing_extensions import override

import discord
from discord.ext import commands

import statalib as lib
from statalib import render2

import helper
from helper.decorators import app_command
from calc.average import AverageStats


@final
class AverageStatsRenderer(render2.RenderingClient):
    def __init__(
        self,
        skin_model_bytes: bytes,
        username: str,
        data: lib.HypixelData,
        mode: lib.Mode
    ) -> None:
        super().__init__(route="average-stats")

        self._skin_model_bytes = skin_model_bytes
        self._username = username
        self._data = data
        self.mode = mode


    @override
    def placeholder_values(self) -> render2.PlaceholderValues:
        mode = self.mode or lib.ModesEnum.OVERALL.value
        stats = AverageStats(self._data, mode)

        xp_progress = stats.leveling.progression

        prestige = lib.render.Prestige(int(stats.level))
        prestige_gradient = prestige.colors.seven_step_gradient

        text_placeholders = {
            "stat_clutch_rate#text": stats.clutch_rate,
            "stat_wins_per_star#text": f"{stats.wins_per_star:,}",
            "stat_losses_per_star#text": f"{stats.losses_per_star:,}",
            "stat_final_kills_per_game#text": f"{stats.final_kills_per_game:,}",
            "stat_final_kills_per_star#text": f"{stats.final_kills_per_star:,}",
            "stat_final_deaths_per_star#text": f"{stats.final_deaths_per_star:,}",
            "stat_beds_broken_per_game#text": f"{stats.beds_broken_per_game:,}",
            "stat_beds_broken_per_star#text": f"{stats.beds_broken_per_star:,}",
            "stat_beds_lost_per_star#text": f"{stats.beds_lost_per_star:,}",
            "stat_kills_per_game#text": f"{stats.kills_per_game:,}",
            "stat_kills_per_star#text": f"{stats.kills_per_star:,}",
            "stat_deaths_per_star#text": f"{stats.deaths_per_star:,}",
            "gamemode#text": mode.name,
            "most_wins_mode#text": stats.most_wins_mode,
            "most_losses_mode#text": stats.most_losses_mode,
        }

        placeholder_values = render2.PlaceholderValues.new(text=text_placeholders)
        placeholder_values.add_progress_bar(prestige_gradient, xp_progress.progress_percent)
        placeholder_values.add_skin_model(self._skin_model_bytes)
        placeholder_values.add_footer_text()
        placeholder_values.add_current_and_next_level(int(stats.level))
        placeholder_values.add_xp_progress_text(stats.leveling.progression)
        placeholder_values.add_playername(stats.rank_info(self._username))

        return placeholder_values


class AverageCommandCog(commands.Cog):
    @app_command(command_id="average")
    @helper.interactions.access_permitted_check()
    async def average(self, interaction: discord.Interaction, player: str | None=None):
        await interaction.response.defer()

        name, uuid = await helper.interactions.fetch_player_info(player, interaction)

        skin_model, hypixel_data = await asyncio.gather(
            lib.network.fetch_skin_model(uuid),
            lib.network.fetch_hypixel_data(uuid)
        )

        renderer = AverageStatsRenderer(skin_model, name, hypixel_data, lib.ModesEnum.OVERALL.value)
        background_img = render2.backgrounds.load_background_for_user(interaction.user.id, "average")
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
    await client.add_cog(AverageCommandCog())
