from statalib.fmt import prefix_int
from statalib.hypixel import (
    BedwarsStats, get_rank_info, mode_name_to_id, rround, ratio)


class CompareStats:
    def __init__(
        self,
        hypixel_data_1: dict,
        hypixel_data_2: dict,
        mode: str='overall'
    ) -> None:
        self._bw_1 = BedwarsStats(hypixel_data_1, ganemode=mode)
        self._bw_2 = BedwarsStats(hypixel_data_2, ganemode=mode)

        self.mode = mode_name_to_id(mode)

        self.level_1 = int(self._bw_1.level)
        self.level_2 = int(self._bw_2.level)

        self.rank_info_1 = get_rank_info(self._bw_1._hypixel_player_data)
        self.rank_info_2 = get_rank_info(self._bw_2._hypixel_player_data)

        self.wins_comp = f'{self._bw_1.wins:,} / {self._bw_2.wins:,}'
        self.wins_diff = prefix_int(self._bw_1.wins - self._bw_2.wins)

        self.losses_comp = f'{self._bw_1.losses:,} / {self._bw_2.losses:,}'
        self.losses_diff = prefix_int(self._bw_1.losses - self._bw_2.losses)

        wlr_1 = ratio(self._bw_1.wins, self._bw_1.losses)
        wlr_2 = ratio(self._bw_2.wins, self._bw_2.losses)

        self.wlr_comp = f'{wlr_1:,} / {wlr_2:,}'
        self.wlr_diff = prefix_int(rround(wlr_1 - wlr_2, 2))


        self.final_kills_comp = \
            f'{self._bw_1.final_kills:,} / {self._bw_2.final_kills:,}'
        self.final_kills_diff = prefix_int(
            self._bw_1.final_kills - self._bw_2.final_kills)

        self.final_deaths_comp = \
            f'{self._bw_1.final_deaths:,} / {self._bw_2.final_deaths:,}'
        self.final_deaths_diff = prefix_int(
            self._bw_1.final_deaths - self._bw_2.final_deaths)

        fkdr_1 = ratio(self._bw_1.final_kills, self._bw_1.final_deaths)
        fkdr_2 = ratio(self._bw_2.final_kills, self._bw_2.final_deaths)

        self.fkdr_comp = f'{fkdr_1:,} / {fkdr_2:,}'
        self.fkdr_diff = prefix_int(rround(fkdr_1 - fkdr_2, 2))


        self.beds_broken_comp = \
            f'{self._bw_1.beds_broken:,} / {self._bw_2.beds_broken:,}'
        self.beds_broken_diff = prefix_int(
            self._bw_1.beds_broken - self._bw_2.beds_broken)

        self.beds_lost_comp = f'{self._bw_1.beds_lost:,} / {self._bw_2.beds_lost:,}'
        self.beds_lost_diff = prefix_int(self._bw_1.beds_lost - self._bw_2.beds_lost)

        bblr_1 = ratio(self._bw_1.beds_broken, self._bw_1.beds_lost)
        bblr_2 = ratio(self._bw_2.beds_broken, self._bw_2.beds_lost)

        self.bblr_comp = f'{bblr_1:,} / {bblr_2:,}'
        self.bblr_diff = prefix_int(rround(bblr_1 - bblr_2, 2))


        self.kills_comp = f'{self._bw_1.kills:,} / {self._bw_2.kills:,}'
        self.kills_diff = prefix_int(self._bw_1.kills - self._bw_2.kills)

        self.deaths_comp = f'{self._bw_1.deaths:,} / {self._bw_2.deaths:,}'
        self.deaths_diff = prefix_int(self._bw_1.deaths - self._bw_2.deaths)

        kdr_1 = ratio(self._bw_1.kills, self._bw_1.deaths)
        kdr_2 = ratio(self._bw_2.kills, self._bw_2.deaths)

        self.kdr_comp = f'{kdr_1:,} / {kdr_2:,}'
        self.kdr_diff = prefix_int(rround(kdr_1 - kdr_2, 2))
