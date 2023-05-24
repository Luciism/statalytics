from calc.calctools import get_player_rank_info, get_mode

class Compare:
    def __init__(self, name_1: str, name_2: str, mode: str, hypixel_data_1: dict, hypixel_data_2) -> None:
        self.name_1, self.name_2 = name_1, name_2
        self.mode = get_mode(mode)

        self.hypixel_data_1 = hypixel_data_1.get('player', {}) if hypixel_data_1.get('player', {}) is not None else {}
        self.hypixel_data_2 = hypixel_data_2.get('player', {}) if hypixel_data_2.get('player', {}) is not None else {}
        self.hypixel_data_bedwars_1 = self.hypixel_data_1.get('stats', {}).get('Bedwars', {})
        self.hypixel_data_bedwars_2 = self.hypixel_data_2.get('stats', {}).get('Bedwars', {})

        self.level_1 = self.hypixel_data_1.get("achievements", {}).get("bedwars_level", 0)
        self.level_2 = self.hypixel_data_2.get("achievements", {}).get("bedwars_level", 0)

        self.player_rank_info = get_player_rank_info(self.hypixel_data_1), get_player_rank_info(self.hypixel_data_2)

    def calc_general_stats(self, key_1, key_2):
        val_1_1 = self.hypixel_data_bedwars_1.get(key_1, 0)
        val_2_1 = self.hypixel_data_bedwars_1.get(key_2, 0)
        ratio_1 = round(0 if val_1_1 == 0 else val_1_1 / val_2_1 if val_2_1 != 0 else val_1_1, 2)

        val_1_2 = self.hypixel_data_bedwars_2.get(key_1, 0)
        val_2_2 = self.hypixel_data_bedwars_2.get(key_2, 0)
        ratio_2 = round(0 if val_1_2 == 0 else val_1_2 / val_2_2 if val_2_2 != 0 else val_1_2, 2)

        val_1_diff = val_1_1 - val_1_2
        val_1_diff = f'{val_1_diff:,}' if val_1_diff < 0 else f'+{val_1_diff:,}'

        val_2_diff = val_2_1 - val_2_2
        val_2_diff = f'{val_2_diff:,}' if val_2_diff < 0 else f'+{val_2_diff:,}'

        ratio_diff = round(ratio_1 - ratio_2, 2)
        ratio_diff = f'{ratio_diff:,}' if ratio_diff < 0 else f'+{ratio_diff:,}'

        return f'{val_1_1:,} / {val_1_2:,}', f'{val_2_1:,} / {val_2_2:,}', f'{ratio_1:,} / {ratio_2:,}', val_1_diff, val_2_diff, ratio_diff

    def get_wins(self):
        return self.calc_general_stats(f'{self.mode}wins_bedwars', f'{self.mode}losses_bedwars')

    def get_finals(self):
        return self.calc_general_stats(f'{self.mode}final_kills_bedwars', f'{self.mode}final_deaths_bedwars')

    def get_beds(self):
        return self.calc_general_stats(f'{self.mode}beds_broken_bedwars', f'{self.mode}beds_lost_bedwars')

    def get_kills(self):
        return self.calc_general_stats(f'{self.mode}kills_bedwars', f'{self.mode}deaths_bedwars')
