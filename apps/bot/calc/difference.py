from statalib.fmt import prefix_int
from statalib.hypixel import CumulativeStats, get_rank_info, ratio
from statalib import rotational_stats as rotational


class DifferenceStats(CumulativeStats):
    def __init__(
        self,
        uuid: str,
        tracker: str,
        hypixel_data: dict,
        mode: str='overall'
    ) -> None:
        rotation_type = rotational.RotationType.from_string(tracker)
        bedwars_stats_snapshot = rotational.RotationalStatsManager(uuid) \
            .get_rotational_data(rotation_type)

        super().__init__(hypixel_data, bedwars_stats_snapshot.data, gamemode=mode)

        self.level = int(self.level)
        self.rank_info = get_rank_info(self._hypixel_player_data)

        self.wlr_old = ratio(self.wins_local, self.losses_local)
        self.wlr_new = ratio(self.wins, self.losses)
        self.wlr_diff = self._ratio_diff(self.wlr_old, self.wlr_new)

        self.fkdr_old = ratio(self.final_kills_local, self.final_deaths_local)
        self.fkdr_new = ratio(self.final_kills, self.final_deaths)
        self.fkdr_diff = self._ratio_diff(self.fkdr_old, self.fkdr_new)

        self.bblr_old = ratio(self.beds_broken_local, self.beds_lost_local)
        self.bblr_new = ratio(self.beds_broken, self.beds_lost)
        self.bblr_diff = self._ratio_diff(self.bblr_old, self.bblr_new)

        self.kdr_old = ratio(self.kills_local, self.deaths_local)
        self.kdr_new = ratio(self.kills, self.deaths)
        self.kdr_diff = self._ratio_diff(self.kdr_old, self.kdr_new)

        self.stars_gained = str(round(self.levels_cum, 2))


    def _ratio_diff(self, old_ratio: float, new_ratio: float):
        ratio_diff = round(new_ratio - old_ratio, 2)
        return f'({prefix_int(ratio_diff)})'
