from statalib.functions import int_prefix
from statalib.calctools import (
    BedwarsStats,
    get_rank_info,
    get_mode,
    rround,
)


class Compare:
    def __init__(
        self,
        hypixel_data_1: dict,
        hypixel_data_2: dict,
        mode: str='overall'
    ) -> None:
        self._bw_1 = BedwarsStats(hypixel_data_1, strict_mode=mode)
        self._bw_2 = BedwarsStats(hypixel_data_2, strict_mode=mode)

        self.mode = get_mode(mode)

        self.level_1 = int(self._bw_1.level)
        self.level_2 = int(self._bw_2.level)

        self.rank_info_1 = get_rank_info(self._bw_1._hypixel_data)
        self.rank_info_2 = get_rank_info(self._bw_2._hypixel_data)


    def _calc_general_stats(self, key_1, key_2):
        val_1_1 = self._bw_1._bedwars_data.get(key_1, 0)
        val_2_1 = self._bw_1._bedwars_data.get(key_2, 0)
        ratio_1 = rround(val_1_1 / (val_2_1 or 1), 2)

        val_1_2 = self._bw_2._bedwars_data.get(key_1, 0)
        val_2_2 = self._bw_2._bedwars_data.get(key_2, 0)
        ratio_2 = rround(val_1_2 / (val_2_2 or 1), 2)

        val_1_diff = val_1_1 - val_1_2
        val_1_diff = f'{int_prefix(val_1_diff)}{val_1_diff:,}'

        val_2_diff = val_2_1 - val_2_2
        val_2_diff = f'{int_prefix(val_2_diff)}{val_2_diff:,}'

        ratio_diff = round(ratio_1 - ratio_2, 2)
        ratio_diff = f'{int_prefix(ratio_diff)}{ratio_diff:,}'

        return f'{val_1_1:,} / {val_1_2:,}', f'{val_2_1:,} / {val_2_2:,}',\
               f'{ratio_1:,} / {ratio_2:,}', val_1_diff, val_2_diff, ratio_diff


    def get_wins(self):
        return self._calc_general_stats(
            f'{self.mode}wins_bedwars', f'{self.mode}losses_bedwars')


    def get_finals(self):
        return self._calc_general_stats(
            f'{self.mode}final_kills_bedwars', f'{self.mode}final_deaths_bedwars')


    def get_beds(self):
        return self._calc_general_stats(
            f'{self.mode}beds_broken_bedwars', f'{self.mode}beds_lost_bedwars')


    def get_kills(self):
        return self._calc_general_stats(
            f'{self.mode}kills_bedwars', f'{self.mode}deaths_bedwars')
