from statalib.calctools import (
    get_rank_info,
    get_mode,
    rround,
    get_level,
    get_player_dict
)


class Compare:
    def __init__(self, name_1: str, name_2: str, mode: str,
                 hypixel_data_1: dict, hypixel_data_2) -> None:
        self.name_1, self.name_2 = name_1, name_2
        self.mode = get_mode(mode)

        self.hypixel_data_1 = get_player_dict(hypixel_data_1)
        self.hypixel_data_2 = get_player_dict(hypixel_data_2)

        self.bedwars_data_1 = self.hypixel_data_1.get('stats', {}).get('Bedwars', {})
        self.bedwars_data_2 = self.hypixel_data_2.get('stats', {}).get('Bedwars', {})

        self.level_1 = int(get_level(self.bedwars_data_1.get('Experience', 0)))
        self.level_2 = int(get_level(self.bedwars_data_2.get('Experience', 0)))

        self.rank_info_1 = get_rank_info(self.hypixel_data_1)
        self.rank_info_2 = get_rank_info(self.hypixel_data_2)


    def _calc_general_stats(self, key_1, key_2):
        val_1_1 = self.bedwars_data_1.get(key_1, 0)
        val_2_1 = self.bedwars_data_1.get(key_2, 0)
        ratio_1 = rround(val_1_1 / (val_2_1 or 1), 2)

        val_1_2 = self.bedwars_data_2.get(key_1, 0)
        val_2_2 = self.bedwars_data_2.get(key_2, 0)
        ratio_2 = rround(val_1_2 / (val_2_2 or 1), 2)

        val_1_diff = val_1_1 - val_1_2
        val_1_diff = f'{val_1_diff:,}' if val_1_diff < 0 else f'+{val_1_diff:,}'

        val_2_diff = val_2_1 - val_2_2
        val_2_diff = f'{val_2_diff:,}' if val_2_diff < 0 else f'+{val_2_diff:,}'

        ratio_diff = round(ratio_1 - ratio_2, 2)
        ratio_diff = f'{ratio_diff:,}' if ratio_diff < 0 else f'+{ratio_diff:,}'

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
