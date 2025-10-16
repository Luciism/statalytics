"""Wrapper for generic hypixel bedwars stats."""

from typing import final

from ..aliases import BedwarsData, HypixelData, HypixelPlayerData
from ..common import Mode
from .leveling import Leveling
from .quests import QuestsDataDict, get_quests_data
from .utils import (
    calc_xp_from_wins,
    get_most_played_mode,
    get_player_dict,
    rround,
)


class BedwarsStats:
    """Wrapper for generic hypixel bedwars stats."""

    def __init__(self, hypixel_data: HypixelData, gamemode: Mode):
        """
        Initialize the class.

        :param hypixel_data: The raw Hypixel API JSON response.
        :param gamemode: The mode to calculate stats for (overall, solos, etc).
        """
        self._gamemode = gamemode
        self._hypixel_player_data: HypixelPlayerData = get_player_dict(hypixel_data)

        self._bedwars_data: BedwarsData = self._hypixel_player_data.get(
            "stats", {}
        ).get("Bedwars", {})

        self.title_mode: str = gamemode.name

        self.wins: int = self._get_mode_stats("wins_bedwars")
        self.losses: int = self._get_mode_stats("losses_bedwars")
        self.wlr: float = self._get_ratio(self.wins, self.losses)

        self.final_kills: int = self._get_mode_stats("final_kills_bedwars")
        self.final_deaths: int = self._get_mode_stats("final_deaths_bedwars")
        self.fkdr: float = self._get_ratio(self.final_kills, self.final_deaths)

        self.beds_broken: int = self._get_mode_stats("beds_broken_bedwars")
        self.beds_lost: int = self._get_mode_stats("beds_lost_bedwars")
        self.bblr: float = self._get_ratio(self.beds_broken, self.beds_lost)

        self.kills: int = self._get_mode_stats("kills_bedwars")
        self.deaths: int = self._get_mode_stats("deaths_bedwars")
        self.kdr: float = self._get_ratio(self.kills, self.deaths)

        self.games_played: int = self._get_mode_stats("games_played_bedwars")
        self.most_played: str = get_most_played_mode(self._bedwars_data)

        self.experience: int = self._bedwars_data.get("Experience", 0)

        self.leveling: Leveling = Leveling(xp=self.experience)
        self.level: float = self.leveling.level

        self.items_purchased: int = self._get_mode_stats("items_purchased_bedwars")
        self.tools_purchased: int = self._get_mode_stats("permanent_items_purchased_bedwars")

        self.resources_collected: int = self._get_mode_stats("resources_collected_bedwars")
        self.iron_collected: int = self._get_mode_stats("iron_resources_collected_bedwars")
        self.gold_collected: int = self._get_mode_stats("gold_resources_collected_bedwars")
        self.diamonds_collected: int = self._get_mode_stats(
            "diamond_resources_collected_bedwars"
        )
        self.emeralds_collected: int = self._get_mode_stats(
            "emerald_resources_collected_bedwars"
        )

        self.loot_chests_regular: int = self._bedwars_data.get("bedwars_boxes", 0)
        self.loot_chests_christmas: int = self._bedwars_data.get(
            "bedwars_christmas_boxes", 0
        )
        self.loot_chests_easter: int = self._bedwars_data.get("bedwars_easter_boxes", 0)
        self.loot_chests_halloween: int = self._bedwars_data.get(
            "bedwars_halloween_boxes", 0
        )
        self.loot_chests_golden: int = self._bedwars_data.get("bedwars_golden_boxes", 0)

        self.loot_chests = int(
            self.loot_chests_regular
            + self.loot_chests_christmas
            + self.loot_chests_easter
            + self.loot_chests_halloween
            + self.loot_chests_golden
        )

        self.coins: int = self._bedwars_data.get("coins", 0)

        self.winstreak: int = self._get_mode_stats("winstreak")
        if self.winstreak is not None:
            self.winstreak_str = f"{self.winstreak:,}"
        else:
            self.winstreak_str = "API Off"
            self.winstreak = 0

        self._quests_data = None

        self._wins_xp_data = None
        self._wins_xp = None

    @property
    def quests_data(self) -> QuestsDataDict:
        """The player's quests data."""
        if self._quests_data is None:
            self._quests_data = get_quests_data(self._hypixel_player_data)
        return self._quests_data

    @property
    def questless_exp(self):
        """Player's exp without exp by quests."""
        return self.quests_data.get("real_exp", 0)

    @property
    def wins_xp_data(self) -> dict[str, int]:
        """The player's wins xp data."""
        if self._wins_xp_data is None:
            self._wins_xp_data = calc_xp_from_wins(self._bedwars_data)
        return self._wins_xp_data

    @property
    def wins_xp(self):
        """XP obtained from wins."""
        return self.wins_xp_data.get("experience", 0)

    def _get_ratio(self, val_1: int, val_2: int):
        return rround(val_1 / (val_2 or 1), 2)

    def _get_mode_stats(self, key: str, default: int = 0) -> int:
        return self._bedwars_data.get(f"{self._gamemode.prefix}{key}", default)
