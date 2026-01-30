import asyncio
import json
import logging
import os
from base64 import b64encode
from datetime import datetime
from io import BytesIO
from typing import Any

import aiohttp
import discord
import statalib as lib
from aiohttp import ClientSession, ClientTimeout
from discord.ext import commands

import helper


async def render_general_stats(placeholder_values: dict[str, dict[str, str | list[dict[str, Any]]]]) -> bytes:
    async with ClientSession(timeout=ClientTimeout(total=10)) as session:
        data = aiohttp.FormData()
        data.add_field(
            "placeholder_values",
            json.dumps(placeholder_values).encode("utf-8"),
            filename="blob",
            content_type="application/json",
        )

        res = await session.post(f"{os.getenv('RENDERER_HOSTNAME')}/bedwars", data=data)
        res.raise_for_status()
        render_bytes = await res.content.read()

    return render_bytes

def rgb_to_hex(rgb: tuple[int, int, int]) -> str:
    def clamp(x: int): 
      return max(0, min(x, 255))

    return "#{0:02x}{1:02x}{2:02x}".format(clamp(rgb[0]), clamp(rgb[1]), clamp(rgb[2]))


def generate_placeholder_values(
    skin_model_b64: str, username: str, data: lib.HypixelData, mode: lib.Mode
) -> dict[str, dict[str, str | list[dict[str, Any]]]]:
    bedwars_stats = lib.hypixel.BedwarsStats(data, mode)
    rank = lib.hypixel.PlayerRank.from_hypixel_data(username, bedwars_stats.hypixel_player_data)
    # rank_info = lib.hypixel.get_rank_info(bedwars_stats.hypixel_player_data)

    now = datetime.now()

    xp_progress = bedwars_stats.leveling.progression

    progress_bar_max_width = 740  # Pixels
    progress_bar_width = progress_bar_max_width * xp_progress.progress_percent / 100

    prestige = lib.render.Prestige(bedwars_stats.leveling.level_int)
    prestige_next = lib.render.Prestige(bedwars_stats.leveling.level_int + 1)

    prestige_gradient = prestige.colors.seven_step_gradient

    return {
        "text": {
            "stat_final_kills#text": [{"value": f"{bedwars_stats.final_kills:,}"}],
            "stat_final_deaths#text": [{"value": f"{bedwars_stats.final_kills:,}"}],
            "stat_fkdr#text": [{"value": f"{bedwars_stats.fkdr:,}"}],
            "stat_wins#text": [{"value": f"{bedwars_stats.wins:,}"}],
            "stat_losses#text": [{"value": f"{bedwars_stats.losses:,}"}],
            "stat_wlr#text": [{"value": f"{bedwars_stats.wlr:,}"}],
            "stat_beds_broken#text": [{"value": f"{bedwars_stats.beds_broken:,}"}],
            "stat_beds_lost#text": [{"value": f"{bedwars_stats.beds_lost:,}"}],
            "stat_bblr#text": [{"value": f"{bedwars_stats.bblr:,}"}],
            "stat_kills#text": [{"value": f"{bedwars_stats.kills:,}"}],
            "stat_deaths#text": [{"value": f"{bedwars_stats.deaths:,}"}],
            "stat_kdr#text": [{"value": f"{bedwars_stats.kdr:,}"}],
            "stat_games_played#text": [{"value": f"{bedwars_stats.games_played:,}"}],
            "stat_most_played#text": [{"value": f"{bedwars_stats.most_played}"}],

            "gamemode#text": [{"value": f"{mode.name}"}],
            "bedwars_tokens#text": [{"value": f"{bedwars_stats.coins:,}"}],
            "slumber_tickets#text": [{"value": f"{bedwars_stats.slumber_tickets:,}"}],

            "level_current#text": [
                {"value": char, "fill": color.hex}
                for char, color in prestige.char_to_color_map()
            ],

            "level_next#text": [
                {"value": char, "fill": color.hex}
                for char, color in prestige_next.char_to_color_map()
            ],

            "xp_progress#text": [{"value": f"{xp_progress.progress:,} / {xp_progress.target:,} xp"}],

            "displayname#text": [
                {"value": part[0], "fill": part[1].hex} for part in rank.parts_with_username
            ],

            "footer_info#text": [
                {"value": "statalytics.net • ", "fill": "#FFFFFF"},
                {"value": now.strftime( f"%A %d{lib.fmt.ordinal(now.day)} %B, %Y"), "fill": "#ABABAB", "font_weight": 300}
            ],
        },
        "images": {
            "skin_model#href": skin_model_b64,
        },
        "shapes": {
            "progress_bar#width": str(progress_bar_width),
            "progress_bar#gradientStop.0": prestige_gradient[0].hex,
            "progress_bar#gradientStop.1": prestige_gradient[1].hex,
            "progress_bar#gradientStop.2": prestige_gradient[2].hex,
            "progress_bar#gradientStop.3": prestige_gradient[3].hex,
            "progress_bar#gradientStop.4": prestige_gradient[4].hex,
            "progress_bar#gradientStop.5": prestige_gradient[5].hex,
            "progress_bar#gradientStop.6": prestige_gradient[6].hex,
        }
    }


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

        skin_model_b64 = f"data:image/png;base64,{b64encode(skin_model).decode('utf-8')}"
        placeholder_values = generate_placeholder_values(
            skin_model_b64, name, hypixel_data, mode=lib.ModesEnum.OVERALL.value
        )
        # logging.info(placeholder_values)
        rendered = await render_general_stats(placeholder_values)
        img_bytes = BytesIO(rendered)
        _ = img_bytes.seek(0)

        await interaction.followup.send(
            files=[discord.File(img_bytes, filename="general.png")]
        )


async def setup(client: helper.Client) -> None:
    await client.add_cog(GeneralBedwarsStatsCog())
