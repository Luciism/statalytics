"""Wrapper for cumulative hypixel bedwars stats."""

from ..aliases import HypixelData
from .bedwars_stats import BedwarsStats
from .utils import BEDWARS_MODES_MAP
from .leveling import Leveling
from ..stats_snapshot import BedwarsStatsSnapshot


class CumulativeStats(BedwarsStats):
    """Cumulative hypixel bedwars stats."""
    def __init__(
        self,
        hypixel_data: HypixelData,
        bedwars_stats_snapshot: BedwarsStatsSnapshot,
        gamemode: str='overall'
    ) -> None:
        """
        Initialize the class.

        :param hypixel_data: The raw Hypixel API JSON response.
        :param bedwars_stats_snapshot: A local bedwars stats snapshot of a player.
        :param gamemode: The mode to calculate stats for (overall, solos, etc).
        """
        super().__init__(hypixel_data, gamemode)

        self._bedwars_stats_snapshot = bedwars_stats_snapshot

        self.wins_local = self._get_mode_stats_local('wins_bedwars')
        self.losses_local = self._get_mode_stats_local('losses_bedwars')

        self.wins_cum = self._calc_cum('wins_bedwars')
        self.losses_cum = self._calc_cum('losses_bedwars')
        self.wlr_cum = self._get_ratio(self.wins_cum, self.losses_cum)

        self.final_kills_local = self._get_mode_stats_local('final_kills_bedwars')
        self.final_deaths_local = self._get_mode_stats_local('final_deaths_bedwars')

        self.final_kills_cum = self._calc_cum('final_kills_bedwars')
        self.final_deaths_cum = self._calc_cum('final_deaths_bedwars')
        self.fkdr_cum = self._get_ratio(self.final_kills_cum, self.final_deaths_cum)

        self.beds_broken_local = self._get_mode_stats_local('beds_broken_bedwars')
        self.beds_lost_local = self._get_mode_stats_local('beds_lost_bedwars')

        self.beds_broken_cum = self._calc_cum('beds_broken_bedwars')
        self.beds_lost_cum = self._calc_cum('beds_lost_bedwars')
        self.bblr_cum = self._get_ratio(self.beds_broken_cum, self.beds_lost_cum)

        self.kills_local = self._get_mode_stats_local('kills_bedwars')
        self.deaths_local = self._get_mode_stats_local('deaths_bedwars')

        self.kills_cum = self._calc_cum('kills_bedwars')
        self.deaths_cum = self._calc_cum('deaths_bedwars')
        self.kdr_cum = self._get_ratio(self.kills_cum, self.deaths_cum)

        self.most_played_cum = self._get_most_played()
        self.games_played_cum = self._calc_cum('games_played_bedwars')

        self.experience_local = self._bedwars_stats_snapshot.Experience
        self.level_local = Leveling(xp=self.experience_local).level

        self.experience_cum = self.experience - self.experience_local
        self.levels_cum = self.level - Leveling(xp=self.experience_local).level

        self.items_purchased_cum = self._calc_cum('items_purchased_bedwars')


    def _get_mode_stats_local(self, key: str, default=0) -> dict | int:
        prefix = BEDWARS_MODES_MAP.get(self._gamemode.lower())
        return self._bedwars_stats_snapshot.__dict__.get(f'{prefix}{key}', default)


    def _calc_cum(self, key: str) -> int:
        hypixel_value = self._get_mode_stats(key)
        local_value = self._get_mode_stats_local(key)

        return hypixel_value - local_value


    def _get_most_played(self):
        modes_dict = {
            'Solos': self._calc_cum('eight_one_games_played_bedwars'),
            'Doubles': self._calc_cum('eight_two_games_played_bedwars'),
            'Threes': self._calc_cum('four_three_games_played_bedwars'),
            'Fours': self._calc_cum('four_four_games_played_bedwars'),
            '4v4': self._calc_cum('two_four_games_played_bedwars')
        }
        if max(modes_dict.values()) == 0:
            return "N/A"
        return str(max(modes_dict, key=modes_dict.get))
