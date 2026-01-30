"""Hypixel rank related functionality."""

from dataclasses import dataclass
from typing import TypedDict

from ..aliases import HypixelPlayerData
from ..cfg import config
from ..color import COLOR_CODE_MAP, STR_TO_COLOR_CODE_MAP, Color 


def _get_default_rank(hypixel_player_data: HypixelPlayerData) -> str:
    """Determine the default rank a player should
    have based off of their Hypixel data."""
    if hypixel_player_data.get("rank"):
        return hypixel_player_data["rank"]

    if hypixel_player_data.get("monthlyPackageRank") == "SUPERSTAR":
        return "MVP_PLUS_PLUS"

    if hypixel_player_data.get("packageRank") or hypixel_player_data.get(
        "newPackageRank"
    ):
        rank_hierarchy = ["MVP_PLUS", "MVP", "VIP_PLUS", "VIP", "NONE"]

        old_package_rank = hypixel_player_data.get("packageRank", "NONE")
        new_package_rank = hypixel_player_data.get("newPackageRank", "NONE")

        # Get highest tier out of old and new package ranks
        return rank_hierarchy[
            min(
                [
                    rank_hierarchy.index(old_package_rank),
                    rank_hierarchy.index(new_package_rank),
                ]
            )
        ]

    return "NONE"


class RankInfo(TypedDict):
    """Information about a player's rank."""

    rank: str
    "The ID of the rank."
    prefix: str
    """The rank prefix of the rank."""
    formatted_prefix: str
    """The color coded rank prefix of the rank."""
    color: str
    """The primary color code of the rank."""
    color_rgb: tuple[int, int, int]
    """The primary RGB color value of the rank."""
    plus_color: str
    """The plus color code of the rank."""


def get_rank_info(hypixel_player_data: HypixelPlayerData) -> RankInfo:
    """
    Get a player's rank information including plus color.

    :param hypixel_player_data: The player data of the Hypixel response.
    """
    player_uuid: str | None = hypixel_player_data.get("uuid")
    plus_color: str = hypixel_player_data.get("rankPlusColor", "RED")

    rank_configs = config("global.ranks")

    if player_uuid and player_uuid.replace("-", "") in rank_configs["custom"]:
        rank = "CUSTOM"
        rank_config = rank_configs["custom"][player_uuid]
    else:
        rank = _get_default_rank(hypixel_player_data)
        rank_config = rank_configs["default"].get(rank, rank_configs["default"]["NONE"])

    return {
        "rank": rank,
        "prefix": rank_config["colored_prefix"],
        "formatted_prefix": rank_config["colored_prefix"].format(
            plus_color=STR_TO_COLOR_CODE_MAP.get(plus_color.upper())
        ),
        "color": rank_config["color"],
        "color_rgb": Color.from_color_code(rank_config["color"]).rgb,
        "plus_color": plus_color,
    }


@dataclass
class PlayerRank:
    rank: str
    prefix: str
    color_coded_prefix: str

    plus_color_code: str
    plus_color: Color

    rank_color_code: str
    rank_color: Color

    username: str

    parts: list[tuple[str, Color]]
    "List of (segment, color)"
    parts_with_username: list[tuple[str, Color]]
    "List of (segment, color)"

    @staticmethod
    def from_hypixel_data(username: str, hypixel_player_data: HypixelPlayerData) -> "PlayerRank":
        player_uuid: str | None = hypixel_player_data.get("uuid")
        plus_color: str = hypixel_player_data.get("rankPlusColor", "RED")

        rank_configs = config("global.ranks")

        if player_uuid and player_uuid.replace("-", "") in rank_configs["custom"]:
            rank = "CUSTOM"
            rank_config = rank_configs["custom"][player_uuid]
        else:
            rank = _get_default_rank(hypixel_player_data)
            rank_config = rank_configs["default"].get(
                rank, rank_configs["default"]["NONE"]
            )

        colored_prefix: str = rank_config["colored_prefix"].format(
            plus_color=STR_TO_COLOR_CODE_MAP.get(plus_color.upper())
        )

        parts = [
            [part[1:], Color.from_color_code(f"&{part[0]}")]
            for part in colored_prefix.split("&") if part
        ]
        parts_with_username = parts.copy()
        parts_with_username[-1][0] += username

        return PlayerRank(
            rank=rank,
            prefix=rank_config["prefix"],
            color_coded_prefix=rank_config["colored_prefix"],
            plus_color_code=STR_TO_COLOR_CODE_MAP[plus_color],
            plus_color=Color.from_color_str(plus_color),

            rank_color_code=rank_config["color"],
            rank_color=Color.from_color_code(rank_config["color"]),

            username=username,
            parts=[tuple(part) for part in parts],
            parts_with_username=[tuple(part) for part in parts_with_username]
        )

