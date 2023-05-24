import math
import sqlite3

from calc.calctools import get_player_rank_info, get_mode

class Stats:
    def __init__(self, name: str, uuid: str, mode: str, session: int, hypixel_data: dict) -> None:
        self.name = name
        self.mode = get_mode(mode)

        with sqlite3.connect('./database/sessions.db') as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM sessions WHERE session=? AND uuid=?", (session, uuid))
            session_data = cursor.fetchone()
            if session_data:
                column_names = [desc[0] for desc in cursor.description]
                self.session_data = dict(zip(column_names, session_data))
            else:
                self.session_data = None

        self.hypixel_data = hypixel_data.get('player', {}) if hypixel_data.get('player', {}) != None else {}
        self.hypixel_data_bedwars = self.hypixel_data.get('stats', {}).get('Bedwars', {})

        self.level = self.hypixel_data.get("achievements", {}).get("bedwars_level", 0)
        self.player_rank_info = get_player_rank_info(self.hypixel_data)

    def calc_general_stats(self, key_1, key_2, ratio):
        val_1 = self.hypixel_data_bedwars.get(key_1, 0)
        val_2 = self.hypixel_data_bedwars.get(key_2, 0)

        target_ratio = math.ceil(0 if val_1 == 0 else val_1 / val_2 if val_2 > 0 else val_1+1)
        val_1_at_ratio = int(val_2 * target_ratio if val_2 > 1 else ((val_1 / (target_ratio - 1 | 1) if target_ratio > 0 else 0) * target_ratio))
        val_1_until_ratio = val_1_at_ratio - val_1

        if self.session_data:
            session_val_1 = val_1 - self.session_data[key_1]
            session_val_2 = val_2 - self.session_data[key_2]

            val_1_repitition = 0 if val_1_until_ratio == 0 else val_1_until_ratio / session_val_1 if session_val_1 != 0 else val_1_until_ratio
            new_val_2 = session_val_2 * val_1_repitition + val_2

            val_1_at_ratio = int(new_val_2 * target_ratio if new_val_2 > 1 else ((val_1 / (target_ratio - 1 | 1) if target_ratio > 0 else 0) * target_ratio))
            val_1_until_ratio = val_1_at_ratio - val_1

        target_val_1 = (val_1 // 1000 + 1) * 1000
        val_1_until_val_1 = target_val_1 - val_1

        target_val_2 = (val_2 // 1000 + 1) * 1000
        val_2_until_val_2 = target_val_2 - val_2

        return f"{val_1_until_ratio:,}", f"{val_1_at_ratio:,}", f"{target_ratio:,} {ratio}", f"{val_1_until_val_1:,}", f"{target_val_1:,}", f"{int(val_2_until_val_2):,}", f"{int(target_val_2):,}"

    def get_wins(self):
        return self.calc_general_stats(f'{self.mode}wins_bedwars', f'{self.mode}losses_bedwars', 'WLR')

    def get_finals(self):
        return self.calc_general_stats(f'{self.mode}final_kills_bedwars', f'{self.mode}final_deaths_bedwars', 'FKDR')

    def get_beds(self):
        return self.calc_general_stats(f'{self.mode}beds_broken_bedwars', f'{self.mode}beds_lost_bedwars', 'BBLR')

    def get_kills(self):
        return self.calc_general_stats(f'{self.mode}kills_bedwars', f'{self.mode}deaths_bedwars', 'KDR')

    def get_stars(self):
        level_target = (self.level // 100 + 1) * 100
        needed_levels = level_target - self.level
        return str(needed_levels), str(level_target)
