import asyncio
from typing import final 
from statalib.hypixel import BedwarsStats
from typing_extensions import override

import discord
import statalib as lib
from discord.ext import commands
from statalib import ModesEnum, render2

from calc.total import TotalStats
import helper


@final
class BedwarsStatsRenderer(render2.RenderingClient):
    def __init__(
        self,
        skin_model_bytes: bytes,
        username: str,
        data: lib.HypixelData,
        mode: lib.Mode
    ) -> None:
        super().__init__(route="bedwars-stats")

        self._skin_model_bytes = skin_model_bytes
        self._username = username
        self._data = data
        self.mode = mode


    @override
    def placeholder_values(self) -> render2.PlaceholderValues:
        mode = self.mode or lib.ModesEnum.OVERALL.value
        stats = BedwarsStats(self._data, mode)

        xp_progress = stats.leveling.progression

        prestige = lib.render.Prestige(int(stats.level))
        prestige_gradient = prestige.colors.seven_step_gradient

        text_placeholders = {
            "stat_wins#text": f"{stats.wins:,}",
            "stat_losses#text": f"{stats.losses:,}",
            "stat_wlr#text": f"{stats.wlr:,}",

            "stat_final_kills#text": f"{stats.final_kills:,}",
            "stat_final_deaths#text": f"{stats.final_deaths:,}",
            "stat_fkdr#text": f"{stats.fkdr:,}",

            "stat_kills#text": f"{stats.kills:,}",
            "stat_deaths#text": f"{stats.deaths:,}",
            "stat_kdr#text": f"{stats.kdr:,}",

            "stat_beds_broken#text": f"{stats.beds_broken:,}",
            "stat_beds_lost#text": f"{stats.beds_lost:,}",
            "stat_bblr#text": f"{stats.bblr:,}",

            "stat_games_played#text": f"{stats.games_played:,}",
            "stat_most_played#text": stats.most_played,

            "gamemode#text": mode.name,
            "bedwars_tokens#text": f"{stats.coins:,}",
            "slumber_tickets#text": f"{stats.slumber_tickets:,}"
        }

        placeholder_values = render2.PlaceholderValues.new(text=text_placeholders)
        placeholder_values.add_progress_bar(prestige_gradient, xp_progress.progress_percent)
        placeholder_values.add_skin_model(self._skin_model_bytes)
        placeholder_values.add_footer_text()
        placeholder_values.add_current_and_next_level(int(stats.level))
        placeholder_values.add_xp_progress_text(stats.leveling.progression)
        placeholder_values.add_playername(stats.rank_info(self._username))

        return placeholder_values

@final
class PointlessStatsRenderer(render2.RenderingClient):
    def __init__(
        self,
        skin_model_bytes: bytes,
        username: str,
        data: lib.HypixelData,
        mode: lib.Mode
    ) -> None:
        super().__init__(route="pointless-stats")

        self._skin_model_bytes = skin_model_bytes
        self._username = username
        self._data = data
        self.mode = mode


    @override
    def placeholder_values(self) -> render2.PlaceholderValues:
        mode = self.mode or lib.ModesEnum.OVERALL.value
        stats = TotalStats(self._data, mode)

        xp_progress = stats.leveling.progression

        prestige = lib.render.Prestige(int(stats.level))
        prestige_gradient = prestige.colors.seven_step_gradient

        text_placeholders = {
            "stat_falling_kills#text": f"{stats.falling_kills:,}",
            "stat_falling_deaths#text": f"{stats.falling_deaths:,}",
            "stat_falling_kdr#text": f"{stats.falling_kdr:,}",

            "stat_void_kills#text": f"{stats.void_kills:,}",
            "stat_void_deaths#text": f"{stats.void_deaths:,}",
            "stat_void_kdr#text": f"{stats.void_kdr:,}",

            "stat_ranged_kills#text": f"{stats.projectile_kills:,}",
            "stat_ranged_deaths#text": f"{stats.projectile_deaths:,}",
            "stat_ranged_kdr#text": f"{stats.projectile_kdr:,}",

            "stat_fire_kills#text": f"{stats.fire_kills:,}",
            "stat_fire_deaths#text": f"{stats.fire_deaths:,}",
            "stat_fire_kdr#text": f"{stats.fire_kdr:,}",

            "stat_regular_melee_kills#text": f"{stats.melee_kills:,}",
            "stat_tools_purchased#text": f"{stats.tools_purchased:,}",

            "gamemode#text": mode.name,
            "bedwars_tokens#text": f"{stats.coins:,}",
            "slumber_tickets#text": f"{stats.slumber_tickets:,}"
        }

        placeholder_values = render2.PlaceholderValues.new(text=text_placeholders)
        placeholder_values.add_progress_bar(prestige_gradient, xp_progress.progress_percent)
        placeholder_values.add_skin_model(self._skin_model_bytes)
        placeholder_values.add_footer_text()
        placeholder_values.add_current_and_next_level(int(stats.level))
        placeholder_values.add_xp_progress_text(stats.leveling.progression)
        placeholder_values.add_playername(stats.get_rank_info(self._username))

        return placeholder_values



class GenericStatsCommandCog(commands.Cog):
    async def total_command(
        self,
        interaction: discord.Interaction,
        player: str | None,
        renderer_type: type[BedwarsStatsRenderer | PointlessStatsRenderer],
        render_name: str,
        dreams: bool = False,
    ):
        await interaction.response.defer()

        name, uuid = await helper.interactions.fetch_player_info(player, interaction)

        skin_model, hypixel_data = await asyncio.gather(
            lib.network.fetch_skin_model(uuid),
            lib.network.fetch_hypixel_data(uuid),
        )

        if not dreams:
            modes = ModesEnum.non_dream_modes()
        else:
            modes = ModesEnum.dream_modes()

        renderer = renderer_type(
            skin_model,
            name,
            hypixel_data,
            modes[0]
        )
        background_img = renderer.bg(interaction.user.id, render_name, uuid)

        await helper.views.FractylModesView(
            interaction_origin=interaction,
            background_img=background_img,
            renderer=renderer,
            modes=modes
        ).send_initial()


    @helper.decorators.app_command("bedwars_general")
    @helper.interactions.access_permitted_check()
    async def total(self, interaction: discord.Interaction, player: str | None = None):
        await self.total_command(interaction, player, BedwarsStatsRenderer, "total")

    @helper.decorators.app_command("bedwars_pointless")
    @helper.interactions.access_permitted_check()
    async def pointless(
        self, interaction: discord.Interaction, player: str | None = None
    ):
        await self.total_command(interaction, player, PointlessStatsRenderer, "total")

    @helper.decorators.app_command("dreams")
    @helper.interactions.access_permitted_check()
    async def dreams(self, interaction: discord.Interaction, player: str | None = None):
        await self.total_command(interaction, player, BedwarsStatsRenderer, "total", dreams=True)


async def setup(client: helper.Client) -> None:
    await client.add_cog(GenericStatsCommandCog())
