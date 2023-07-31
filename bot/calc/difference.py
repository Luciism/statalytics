import sqlite3

from statalib.functions import prefix_int
from statalib.calctools import (
    BedwarsStats,
    get_rank_info,
    get_mode,
    get_level
)


class DifferenceStats(BedwarsStats):
    def __init__(
        self,
        uuid: str,
        tracker: str,
        hypixel_data: dict,
        mode: str='overall'
    ) -> None:
        super().__init__(hypixel_data, strict_mode=mode)

        self.mode = get_mode(mode)

        self.level = int(self.level)
        self.rank_info = get_rank_info(self._hypixel_data)

        with sqlite3.connect('./database/core.db') as conn:
            cursor = conn.cursor()

            cursor.execute(
                "SELECT * FROM trackers WHERE uuid = ? and tracker = ?", (uuid, tracker))
            historic_data = cursor.fetchone()

            column_names = [desc[0] for desc in cursor.description]
            self.historic_data = dict(zip(column_names, historic_data))


    def _calc_general_stats(self, key_1, key_2):
        val_1_hypixel = self._bedwars_data.get(key_1, 0)
        val_2_hypixel = self._bedwars_data.get(key_2, 0)

        val_1_historic = self.historic_data[key_1]
        val_2_historic = self.historic_data[key_2]

        val_1_gained = val_1_hypixel - val_1_historic
        val_2_gained = val_2_hypixel - val_2_historic

        current_ratio = round(val_1_hypixel / (val_2_hypixel or 1), 2)
        old_ratio = round(val_1_historic / (val_2_historic or 1), 2)

        ratio_diff = round(current_ratio - old_ratio, 2)
        ratio_diff = f'({prefix_int(ratio_diff)})'

        return (f'{val_1_gained:,}', f'{val_2_gained:,}',
                f'{old_ratio:,}', f'{current_ratio:,}', ratio_diff)


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


    def get_stars_gained(self):
        exp_hypixel = self.experience
        exp_historical = self.historic_data['Experience']
        stars_gained = get_level(exp_hypixel) - get_level(exp_historical)
        return str(round(stars_gained, 2))
