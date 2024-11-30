"""Utility functions for rotational stats."""

def get_bedwars_data(hypixel_data: dict) -> dict:
    """Safely get the player's Bedwars stats data."""
    hypixel_data = hypixel_data.get("player", {}) or {}
    bedwars_data: dict = hypixel_data.get("stats", {}).get("Bedwars", {})

    return bedwars_data
