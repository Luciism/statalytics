"""Hypixel rank related functionality."""

from typing import TypedDict

from ..cfg import config
from ..color import ColorMappings


def _get_default_rank(hypixel_data: dict) -> str:
    """Determine the default rank a player should
    have based off of their Hypixel data."""
    if hypixel_data.get("rank"):
        return hypixel_data["rank"]

    if hypixel_data.get("monthlyPackageRank") == "SUPERSTAR":
        return "MVP_PLUS_PLUS"

    if hypixel_data.get("packageRank") or hypixel_data.get("newPackageRank"):
        rank_hierarchy = ["MVP_PLUS", "MVP", "VIP_PLUS", "VIP", "NONE"]

        old_package_rank = hypixel_data.get("packageRank", "NONE")
        new_package_rank = hypixel_data.get("newPackageRank", "NONE")

        # Get highest tier out of old and new package ranks
        return rank_hierarchy[min([
            rank_hierarchy.index(old_package_rank),
            rank_hierarchy.index(new_package_rank)
        ])]

    return "NONE"


class RankInfo(TypedDict):
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


def get_rank_info(hypixel_data: dict) -> RankInfo:
    """
    Get a player's rank information including plus color.

    :param hypixel_data: The Hypixel player data of the player.
    """
    player_uuid: str | None = hypixel_data.get('uuid')
    plus_color: str = hypixel_data.get("rankPlusColor", "RED")

    rank_configs = config("global.ranks")

    if player_uuid and player_uuid.replace("-", "") in rank_configs["custom"]:
        rank = "CUSTOM"
        rank_config = rank_configs["custom"][player_uuid]
    else:
        rank = _get_default_rank(hypixel_data)
        rank_config = rank_configs["default"]\
            .get(rank, rank_configs["default"]["NONE"])

    return {
        "rank": rank,
        "prefix": rank_config["prefix"],
        "formatted_prefix": rank_config["prefix"].format(
            plus_color=ColorMappings.str_to_color_code.get(plus_color.lower())),
        "color": rank_config["color"],
        "color_rgb": ColorMappings.color_codes.get(rank_config["color"]),
        "plus_color": plus_color
    }
