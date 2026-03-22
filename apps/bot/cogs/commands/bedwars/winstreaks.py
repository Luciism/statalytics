import asyncio
from typing import final
from statalib import render2
from typing_extensions import override

import discord
from discord.ext import commands

import statalib as lib
from calc.winstreaks import WinstreakStats
import helper

@final
class WinstreakStatsRenderer(render2.RenderingClient):
    def __init__(
        self,
        skin_model_bytes: bytes,
        username: str,
        data: lib.HypixelData,
    ) -> None:
        super().__init__(route="winstreaks")

        self._skin_model_bytes = skin_model_bytes
        self._username = username
        self._data = data


    @override
    def placeholder_values(self) -> render2.PlaceholderValues:
        stats = WinstreakStats(self._data)

        xp_progress = stats.leveling.progression

        prestige = lib.render.Prestige(int(stats.level))
        prestige_gradient = prestige.colors.seven_step_gradient

        text_placeholders = {
            "winstreak_overall#text": f"{stats.winstreak_overall}",
            "winstreak_solos#text": f"{stats.winstreak_solos}",
            "winstreak_doubles#text": f"{stats.winstreak_doubles}",
            "winstreak_threes#text": f"{stats.winstreak_threes}",
            "winstreak_fours#text": f"{stats.winstreak_fours}",
            "winstreak_4v4#text": f"{stats.winstreak_4v4}",

            "total_wins#text": f"{stats.wins:,}",
            "api_status#text": f"{stats.api_status}",
        }

        placeholder_values = render2.PlaceholderValues.new(text=text_placeholders)
        placeholder_values.add_progress_bar(prestige_gradient, xp_progress.progress_percent)
        placeholder_values.add_skin_model(self._skin_model_bytes)
        placeholder_values.add_footer_text()
        placeholder_values.add_current_and_next_level(int(stats.level))
        placeholder_values.add_xp_progress_text(stats.leveling.progression)
        placeholder_values.add_playername(stats.get_rank_info(self._username))

        return placeholder_values



class WinstreaksCommandCog(commands.Cog):
    @helper.decorators.app_command("winstreaks")
    @helper.interactions.access_permitted_check()
    async def winstreaks(self, interaction: discord.Interaction, player: str | None=None):
        await interaction.response.defer()

        name, uuid = await helper.interactions.fetch_player_info(player, interaction)

        skin_model, hypixel_data = await asyncio.gather(
            lib.network.fetch_skin_model(uuid),
            lib.network.fetch_hypixel_data(uuid)
        )

        renderer = WinstreakStatsRenderer(skin_model, name, hypixel_data)

        background_img = render2.backgrounds.load_background_for_user(interaction.user.id, "winstreaks")
        img_bytes = await renderer.render_to_buffer(background_img)
        
        await interaction.followup.send(
            files=[discord.File(img_bytes, filename="winstreaks.png")],
        )


async def setup(client: helper.Client) -> None:
    await client.add_cog(WinstreaksCommandCog())
