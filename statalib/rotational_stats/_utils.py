"""Utility functions for rotational stats."""

from ..aliases import HypixelData, BedwarsData

def get_bedwars_data(hypixel_data: HypixelData) -> BedwarsData:
    """Safely get the player's Bedwars stats data."""
    hypixel_player_data = hypixel_data.get("player", {}) or {}
    bedwars_data = hypixel_player_data.get("stats", {}).get("Bedwars", {})

    return bedwars_data
