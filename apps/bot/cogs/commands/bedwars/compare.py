import asyncio
from typing import Literal, final

import discord
import statalib as lib
from discord.ext import commands
from statalib import render2
from statalib.hypixel import rround
from typing_extensions import override

import helper
from calc.compare import CompareStats, StatDifference


def generate_value_text(
    stat: StatDifference, stat_type: Literal["good", "bad", "ratio"]
) -> list[render2.TSpan]:
    if stat_type == "good":
        value_color = "{variable:colors.positive}"
    elif stat_type == "bad":
        value_color = "{variable:colors.negative}"
    else:
        value_color = "{variable:colors.primary}"

    return [
        render2.TSpan(value=f"{stat.value1:,}", fill=value_color),
        render2.TSpan(value=" / ", fill="{variable:colors.text}"),
        render2.TSpan(value=f"{stat.value2:,}", fill=value_color),
    ]


def generate_delta_text(
    stat: StatDifference, stat_type: Literal["good", "bad", "ratio"]
) -> render2.TSpan:
    if stat.delta >= 0:
        if stat_type == "good" or stat_type == "ratio":
            delta_color = "{variable:colors.positive}"
        else:
            delta_color = "{variable:colors.negative}"
    else:
        if stat_type == "good" or stat_type == "ratio":
            delta_color = "{variable:colors.negative}"
        else:
            delta_color = "{variable:colors.positive}"

    return render2.TSpan(value=f"{stat.symbol}{rround(stat.delta, 2):,}", fill=delta_color)


@final
class StatComparisonRenderer(render2.RenderingClient):
    def __init__(
        self,
        skin_model1_bytes: bytes,
        skin_model2_bytes: bytes,
        username1: str,
        username2: str,
        data1: lib.HypixelData,
        data2: lib.HypixelData,
        mode: lib.Mode,
    ) -> None:
        super().__init__(route="stat-comparison")

        self._skin_model1_bytes = skin_model1_bytes
        self._skin_model2_bytes = skin_model2_bytes
        self._username1 = username1
        self._username2 = username2
        self._data1 = data1
        self._data2 = data2
        self.mode = mode

    @override
    def placeholder_values(self) -> render2.PlaceholderValues:
        mode = self.mode or lib.ModesEnum.OVERALL.value
        stats = CompareStats(self._data1, self._data2, mode)

        text_placeholders = {
            "header_text#text": f"Stat Comparison ({mode.name})",
            "stat_wins#text": generate_value_text(stats.wins, "good"),
            "stat_wins_diff#text": generate_delta_text(stats.wins, "good"),
            "stat_losses#text": generate_value_text(stats.losses, "bad"),
            "stat_losses_diff#text": generate_delta_text(stats.losses, "bad"),
            "stat_wlr#text": generate_value_text(stats.wlr, "ratio"),
            "stat_wlr_diff#text": generate_delta_text(stats.wlr, "ratio"),
            "stat_kills#text": generate_value_text(stats.kills, "good"),
            "stat_kills_diff#text": generate_delta_text(stats.kills, "good"),
            "stat_deaths#text": generate_value_text(stats.deaths, "bad"),
            "stat_deaths_diff#text": generate_delta_text(stats.deaths, "bad"),
            "stat_kdr#text": generate_value_text(stats.kdr, "ratio"),
            "stat_kdr_diff#text": generate_delta_text(stats.kdr, "ratio"),
            "stat_final_kills#text": generate_value_text(stats.final_kills, "good"),
            "stat_final_kills_diff#text": generate_delta_text(
                stats.final_kills, "good"
            ),
            "stat_final_deaths#text": generate_value_text(stats.final_deaths, "bad"),
            "stat_final_deaths_diff#text": generate_delta_text(
                stats.final_deaths, "bad"
            ),
            "stat_fkdr#text": generate_value_text(stats.fkdr, "ratio"),
            "stat_fkdr_diff#text": generate_delta_text(stats.fkdr, "ratio"),
            "stat_beds_broken#text": generate_value_text(stats.beds_broken, "good"),
            "stat_beds_broken_diff#text": generate_delta_text(
                stats.beds_broken, "good"
            ),
            "stat_beds_lost#text": generate_value_text(stats.beds_lost, "bad"),
            "stat_beds_lost_diff#text": generate_delta_text(stats.beds_lost, "bad"),
            "stat_bblr#text": generate_value_text(stats.bblr, "ratio"),
            "stat_bblr_diff#text": generate_delta_text(stats.bblr, "ratio"),
        }

        placeholder_values = render2.PlaceholderValues.new(text=text_placeholders)
        placeholder_values.add_skin_model(self._skin_model1_bytes, "skin_model1")
        placeholder_values.add_skin_model(self._skin_model2_bytes, "skin_model2")
        placeholder_values.add_current_level(int(stats.level_1), "player1_level")
        placeholder_values.add_current_level(int(stats.level_2), "player2_level")
        placeholder_values.add_playername(
            stats.get_rank_info_1(self._username1), "displayname1"
        )
        placeholder_values.add_playername(
            stats.get_rank_info_2(self._username2), "displayname2"
        )
        placeholder_values.add_footer_text()

        return placeholder_values


class CompareCommandCog(commands.Cog):
    @helper.decorators.app_command(command_id="compare")
    @helper.interactions.access_permitted_check()
    async def compare(
        self,
        interaction: discord.Interaction,
        player_1: str,
        player_2: str | None = None,
    ):
        await interaction.response.defer()

        name_1 = player_1 if player_2 else None
        name_2 = player_2 if player_2 else player_1

        name_1, uuid_1 = await helper.interactions.fetch_player_info(
            name_1, interaction
        )
        name_2, uuid_2 = await helper.interactions.fetch_player_info(
            name_2, interaction
        )

        hypixel_data_1, hypixel_data_2, skin_model_1, skin_model_2 = (
            await asyncio.gather(
                lib.network.fetch_hypixel_data(uuid_1),
                lib.network.fetch_hypixel_data(uuid_2),
                lib.network.fetch_skin_model(uuid_1),
                lib.network.fetch_skin_model(uuid_2),
            )
        )

        renderer = StatComparisonRenderer(
            skin_model_1,
            skin_model_2,
            name_1,
            name_2,
            hypixel_data_1,
            hypixel_data_2,
            mode=lib.ModesEnum.OVERALL.value,
        )
        background_img = render2.backgrounds.load_background_for_user(interaction.user.id, "stat-comparison")
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
    await client.add_cog(CompareCommandCog())
