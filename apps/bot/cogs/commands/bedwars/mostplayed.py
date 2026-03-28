import asyncio
from typing import final
from statalib import render2
from typing_extensions import override
import discord
from discord.ext import commands

import statalib as lib
from calc.mostplayed import MostPlayedStats
import helper



@final
class MostPlayedModesRenderer(render2.RenderingClient):
    def __init__(
        self,
        skin_model_bytes: bytes,
        username: str,
        data: lib.HypixelData,
    ) -> None:
        super().__init__(route="most-played")

        self._skin_model_bytes = skin_model_bytes
        self._username = username
        self._data = data


    @override
    def placeholder_values(self) -> render2.PlaceholderValues:
        stats = MostPlayedStats(self._data)

        shape_placeholders = {
            "bar_solos#height": f"{stats.solos_bar_height}%",
            "bar_doubles#height": f"{stats.doubles_bar_height}%",
            "bar_threes#height": f"{stats.threes_bar_height}%",
            "bar_fours#height": f"{stats.fours_bar_height}%",
        }

        xp_progress = stats.leveling.progression

        prestige = lib.render.Prestige(int(stats.level))
        prestige_gradient = prestige.colors.seven_step_gradient

        placeholder_values = render2.PlaceholderValues.new(shapes=shape_placeholders)
        placeholder_values.add_skin_model(self._skin_model_bytes)
        placeholder_values.add_footer_text()
        placeholder_values.add_progress_bar(prestige_gradient, xp_progress.progress_percent)
        placeholder_values.add_playername(stats.get_rank_info(self._username))

        return placeholder_values


class MostPlayedCommandCog(commands.Cog):
    @helper.decorators.app_command("gamemode_distributions")
    @helper.interactions.access_permitted_check()
    async def most_played(self, interaction: discord.Interaction, player: str | None=None):
        await interaction.response.defer()

        name, uuid = await helper.interactions.fetch_player_info(player, interaction)

        hypixel_data, skin_model = await asyncio.gather(
            lib.network.fetch_hypixel_data(uuid),
            lib.network.fetch_skin_model(uuid)
        )

        renderer = MostPlayedModesRenderer(skin_model, name, hypixel_data)
        background_img = renderer.bg(interaction.user.id, "mostplayed", uuid)
        img_bytes = await renderer.render_to_buffer(background_img)
        
        await interaction.followup.send(
            files=[discord.File(img_bytes, filename="mostplayed.png")],
        )


async def setup(client: helper.Client) -> None:
    await client.add_cog(MostPlayedCommandCog())
