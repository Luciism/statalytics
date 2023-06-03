import sqlite3

from helper.calctools import get_player_rank_info, get_mode, get_progress, get_level
from helper.functions import uuid_to_discord_id


class Difference:
    def __init__(self, name: str, uuid: str, method: str,
                 mode: str, hypixel_data: dict) -> None:
        self.name = name
        self.mode = get_mode(mode)

        discord_id = uuid_to_discord_id(uuid)

        with sqlite3.connect('./database/historical.db') as conn:
            cursor = conn.cursor()
            if discord_id:
                cursor.execute(f"SELECT * FROM configuration WHERE discord_id = '{discord_id}'")
                self.config_data = cursor.fetchone()
            else:
                self.config_data = ()

            cursor.execute(f"SELECT * FROM {method} WHERE uuid = '{uuid}'")
            historical_data = cursor.fetchone()

            column_names = [desc[0] for desc in cursor.description]
            self.historical_data = dict(zip(column_names, historical_data))

        self.hypixel_data = hypixel_data.get('player', {}) if hypixel_data.get('player', {}) is not None else {}
        self.hypixel_data_bedwars = self.hypixel_data.get('stats', {}).get('Bedwars', {})

        self.level = self.hypixel_data.get("achievements", {}).get("bedwars_level", 0)
        self.games_played = self.hypixel_data_bedwars.get(f'{self.mode}games_played_bedwars', 0)
        self.player_rank_info = get_player_rank_info(self.hypixel_data)
        self.progress = get_progress(hypixel_data_bedwars=self.hypixel_data_bedwars)


    def calc_general_stats(self, key_1, key_2):
        val_1_hypixel = self.hypixel_data_bedwars.get(key_1, 0)
        val_2_hypixel = self.hypixel_data_bedwars.get(key_2, 0)

        val_1_historical = self.historical_data[key_1]
        val_2_historical = self.historical_data[key_2]

        val_1_gained = val_1_hypixel - val_1_historical
        val_2_gained = val_2_hypixel - val_2_historical

        current_ratio = val_1_hypixel / (val_2_hypixel or 1)
        old_ratio = val_1_historical / (val_2_historical or 1)

        ratio_diff = current_ratio - old_ratio
        ratio_diff = f'({"+" if ratio_diff >= 0 else ""}{round(ratio_diff, 2)})'

        return (f'{val_1_gained:,}', f'{val_2_gained:,}',
                f'{round(old_ratio, 2):,}', f'{round(current_ratio, 2):,}', ratio_diff)


    def get_wins(self):
        return self.calc_general_stats(f'{self.mode}wins_bedwars', f'{self.mode}losses_bedwars')


    def get_finals(self):
        return self.calc_general_stats(f'{self.mode}final_kills_bedwars', f'{self.mode}final_deaths_bedwars')


    def get_beds(self):
        return self.calc_general_stats(f'{self.mode}beds_broken_bedwars', f'{self.mode}beds_lost_bedwars')


    def get_kills(self):
        return self.calc_general_stats(f'{self.mode}kills_bedwars', f'{self.mode}deaths_bedwars')


    def get_stars_gained(self):
        experience_hypixel = self.hypixel_data_bedwars.get('Experience', 0)
        experience_historical = self.historical_data['Experience']
        stars_gained = get_level(experience_hypixel) - get_level(experience_historical)
        return str(round(stars_gained, 2))
