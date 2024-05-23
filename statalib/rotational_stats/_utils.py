def get_bedwars_data(hypixel_data: dict) -> dict:
    hypixel_data = hypixel_data.get("player", {}) or {}
    bedwars_data: dict = hypixel_data.get("stats", {}).get("Bedwars", {})

    return bedwars_data
