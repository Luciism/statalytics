import asyncio
from typing import final
from statalib import render2
from typing_extensions import override
import discord
from discord.ext import commands

import statalib as lib
from calc.resources import ResourcesStats
import helper


@final
class ResourceStatsRenderer(render2.RenderingClient):
    def __init__(
        self,
        skin_model_bytes: bytes,
        username: str,
        data: lib.HypixelData,
        mode: lib.Mode
    ) -> None:
        super().__init__(route="resources-collected")

        self._skin_model_bytes = skin_model_bytes
        self._username = username
        self._data = data
        self.mode = mode


    @override
    def placeholder_values(self) -> render2.PlaceholderValues:
        mode = self.mode or lib.ModesEnum.OVERALL.value
        stats = ResourcesStats(self._data, mode)

        xp_progress = stats.leveling.progression

        prestige = lib.render.Prestige(int(stats.level))
        prestige_gradient = prestige.colors.seven_step_gradient


        text_placeholders = {
            "stat_iron_collected#text": f"{stats.iron.collected:,}",
            "stat_gold_collected#text": f"{stats.gold.collected:,}",
            "stat_diamonds_collected#text": f"{stats.diamonds.collected:,}",
            "stat_emeralds_collected#text": f"{stats.emeralds.collected:,}",

            "stat_iron_per_game#text": f"{stats.iron.per_game:,}",
            "stat_gold_per_game#text": f"{stats.gold.per_game:,}",
            "stat_diamonds_per_game#text": f"{stats.diamonds.per_game:,}",
            "stat_emeralds_per_game#text": f"{stats.emeralds.per_game:,}",

            "stat_iron_per_star#text": f"{stats.iron.per_star:,}",
            "stat_gold_per_star#text": f"{stats.gold.per_star:,}",
            "stat_diamonds_per_star#text": f"{stats.diamonds.per_star:,}",
            "stat_emeralds_per_star#text": f"{stats.emeralds.per_star:,}",

            "gamemode#text": mode.name,
            "total_resources_collected#text": f"{stats.resources_collected:,}"
        }

        placeholder_values = render2.PlaceholderValues.new(text=text_placeholders)
        placeholder_values.add_progress_bar(prestige_gradient, xp_progress.progress_percent)
        placeholder_values.add_skin_model(self._skin_model_bytes)
        placeholder_values.add_footer_text()
        placeholder_values.add_current_and_next_level(int(stats.level))
        placeholder_values.add_xp_progress_text(stats.leveling.progression)
        placeholder_values.add_playername(stats.get_rank_info(self._username))

        return placeholder_values



class ResourcesCommandCog(commands.Cog):
    @helper.decorators.app_command("resources")
    @helper.interactions.access_permitted_check()
    async def resources(self, interaction: discord.Interaction, player: str | None=None):
        await interaction.response.defer()

        name, uuid = await helper.interactions.fetch_player_info(player, interaction)

        hypixel_data, skin_model = await asyncio.gather(
            lib.network.fetch_hypixel_data(uuid),
            lib.network.fetch_skin_model(uuid)
        )

        renderer = ResourceStatsRenderer(skin_model, name, hypixel_data, lib.ModesEnum.OVERALL.value)
        background_img = renderer.bg(interaction.user.id, "resources", uuid)
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
    await client.add_cog(ResourcesCommandCog())
