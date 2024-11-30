"""Wrapper for generic hypixel bedwars stats."""

from ..aliases import HypixelData, BedwarsData
from .utils import (
    get_player_dict,
    real_title_case,
    get_most_played_mode,
    calc_xp_from_wins,
    rround,
    BEDWARS_MODES_MAP
)
from .leveling import Leveling
from .quests import get_quests_data


class BedwarsStats:
    """Wrapper for generic hypixel bedwars stats."""
    def __init__(self, hypixel_data: HypixelData, ganemode: str='overall'):
        """
        Initialize the class.

        :param hypixel_data: The raw Hypixel API JSON response.
        :param gamemode: The mode to calculate stats for (overall, solos, etc).
        """
        self._gamemode = ganemode
        self._hypixel_player_data = get_player_dict(hypixel_data)

        self._bedwars_data: BedwarsData = \
            self._hypixel_player_data.get('stats', {}).get('Bedwars', {})

        self.title_mode = real_title_case(ganemode)

        self.wins = self._get_mode_stats('wins_bedwars')
        self.losses = self._get_mode_stats('losses_bedwars')
        self.wlr = self._get_ratio(self.wins, self.losses)

        self.final_kills = self._get_mode_stats('final_kills_bedwars')
        self.final_deaths = self._get_mode_stats('final_deaths_bedwars')
        self.fkdr = self._get_ratio(self.final_kills, self.final_deaths)

        self.beds_broken = self._get_mode_stats('beds_broken_bedwars')
        self.beds_lost = self._get_mode_stats('beds_lost_bedwars')
        self.bblr = self._get_ratio(self.beds_broken, self.beds_lost)

        self.kills = self._get_mode_stats('kills_bedwars')
        self.deaths = self._get_mode_stats('deaths_bedwars')
        self.kdr = self._get_ratio(self.kills, self.deaths)

        self.games_played = self._get_mode_stats('games_played_bedwars')
        self.most_played = get_most_played_mode(self._bedwars_data)

        self.experience = self._bedwars_data.get('Experience', 0)

        self.leveling = Leveling(xp=self.experience)
        self.level = self.leveling.level

        self.items_purchased = self._get_mode_stats('items_purchased_bedwars')
        self.tools_purchased = self._get_mode_stats('permanent_items_purchased_bedwars')

        self.resources_collected = self._get_mode_stats('resources_collected_bedwars')
        self.iron_collected = self._get_mode_stats('iron_resources_collected_bedwars')
        self.gold_collected = self._get_mode_stats('gold_resources_collected_bedwars')
        self.diamonds_collected = self._get_mode_stats('diamond_resources_collected_bedwars')
        self.emeralds_collected = self._get_mode_stats('emerald_resources_collected_bedwars')

        self.loot_chests_regular = self._bedwars_data.get('bedwars_boxes', 0)
        self.loot_chests_christmas = self._bedwars_data.get('bedwars_christmas_boxes', 0)
        self.loot_chests_easter = self._bedwars_data.get('bedwars_easter_boxes', 0)
        self.loot_chests_halloween = self._bedwars_data.get('bedwars_halloween_boxes', 0)
        self.loot_chests_golden = self._bedwars_data.get('bedwars_golden_boxes', 0)

        self.loot_chests = int(self.loot_chests_regular + self.loot_chests_christmas +
            self.loot_chests_easter + self.loot_chests_halloween + self.loot_chests_golden)

        self.coins = self._bedwars_data.get('coins', 0)

        self.winstreak = self._get_mode_stats('winstreak')
        if self.winstreak is not None:
            self.winstreak_str = f'{self.winstreak:,}'
        else:
            self.winstreak_str = 'API Off'
            self.winstreak = 0

        self._quests_data = None

        self._wins_xp_data = None
        self._wins_xp = None


    @property
    def quests_data(self):
        if self._quests_data is None:
            self._quests_data = get_quests_data(self._hypixel_player_data)
        return self._quests_data

    @property
    def questless_exp(self):
        """Player's exp without exp by quests."""
        return self.quests_data.get('real_exp', 0)

    @property
    def wins_xp_data(self):
        if self._wins_xp_data is None:
            self._wins_xp_data = calc_xp_from_wins(self._bedwars_data)
        return self._wins_xp_data

    @property
    def wins_xp(self):
        """XP obtained from wins."""
        return self.wins_xp_data.get('experience', 0)


    def _get_ratio(self, val_1: int, val_2: int):
        return rround(val_1 / (val_2 or 1), 2)


    def _get_mode_stats(self, key: str, default=0) -> int:
        prefix = BEDWARS_MODES_MAP.get(self._gamemode.lower())
        return self._bedwars_data.get(f'{prefix}{key}', default)
