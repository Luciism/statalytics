import sqlite3

from statalib.historical import get_reset_time
from statalib.functions import prefix_int
from statalib.calctools import (
    BedwarsStats,
    get_rank_info,
    get_mode,
    rround,
    get_level,
    xp_from_level
)


hour_list = [
    '12:00am', '1:00am', '2:00am', '3:00am', '4:00am', '5:00am', '6:00am', '7:00am',
    '8:00am', '9:00am', '10:00am', '11:00am', '12:00pm', '1:00pm', '2:00pm', '3:00pm',
    '4:00pm', '5:00pm', '6:00pm', '7:00pm', '8:00pm', '9:00pm', '10:00pm', '11:00pm'
]


class HistoricalStats(BedwarsStats):
    def __init__(
        self,
        uuid: str,
        identifier: int,
        hypixel_data: dict,
        mode: str='overall'
    ) -> None:
        super().__init__(hypixel_data, strict_mode=mode)
        self.uuid = uuid
        self.mode = get_mode(mode)

        with sqlite3.connect('./database/core.db') as conn:
            cursor = conn.cursor()

            cursor.execute(
                "SELECT * FROM trackers WHERE uuid = ? and tracker = ?", (uuid, identifier))
            historic_data = cursor.fetchone()

            column_names = [desc[0] for desc in cursor.description]
            self.historic_data = dict(zip(column_names, historic_data))

        level_local = get_level(self.historic_data['Experience'])
        self.stars_gained = f'{rround(self.level - level_local, 2):,}'
        self.level = int(self.level)


        self.items_purchased = (self.items_purchased -
                                self.historic_data[f'{self.mode}items_purchased_bedwars'])

        self.games_played = (self.games_played -
                             self.historic_data[f'{self.mode}games_played_bedwars'])

        self.rank_info = get_rank_info(self._hypixel_data)


    def get_most_played(self):
        solos = (self._bedwars_data.get('eight_one_games_played_bedwars', 0)
                 - self.historic_data['eight_one_games_played_bedwars'])

        doubles = (self._bedwars_data.get('eight_two_games_played_bedwars', 0)
                   - self.historic_data['eight_two_games_played_bedwars'])

        threes = (self._bedwars_data.get('four_three_games_played_bedwars', 0)
                  - self.historic_data['four_three_games_played_bedwars'])

        fours = (self._bedwars_data.get('four_four_games_played_bedwars', 0)
                 - self.historic_data['four_four_games_played_bedwars'])

        four_vs_four = (self._bedwars_data.get('two_four_games_played_bedwars', 0)
                        - self.historic_data['two_four_games_played_bedwars'])

        modes_dict = {
            'Solos': solos,
            'Doubles': doubles,
            'Threes':  threes,
            'Fours': fours,
            '4v4': four_vs_four
        }
        if max(modes_dict.values()) == 0:
            return "N/A"
        return str(max(modes_dict, key=modes_dict.get))


    def _calc_general_stats(self, key_1, key_2):
        val_1 = self._bedwars_data.get(key_1, 0) - self.historic_data[key_1]
        val_2 = self._bedwars_data.get(key_2, 0) - self.historic_data[key_2]
        ratio = rround(val_1 / (val_2 or 1), 2)
        return f'{val_1:,}', f'{val_2:,}', f'{ratio:,}'


    def get_wins(self):
        return self._calc_general_stats(
            f'{self.mode}wins_bedwars', f'{self.mode}losses_bedwars')


    def get_finals(self):
        return self._calc_general_stats(
            f'{self.mode}final_kills_bedwars', f'{self.mode}final_deaths_bedwars')


    def get_kills(self):
        return self._calc_general_stats(
            f'{self.mode}kills_bedwars', f'{self.mode}deaths_bedwars')


    def get_beds(self):
        return self._calc_general_stats(
            f'{self.mode}beds_broken_bedwars', f'{self.mode}beds_lost_bedwars')


    def get_time_info(self):
        gmt_offset, hour = get_reset_time(self.uuid)

        timezone = f'GMT{prefix_int(gmt_offset)}:00'
        reset_hour = hour_list[hour]

        return timezone, reset_hour


class LookbackStats(BedwarsStats):
    def __init__(
        self,
        uuid: str,
        period: str,
        hypixel_data: dict,
        mode: str='overall'
    ) -> None:
        super().__init__(hypixel_data, strict_mode=mode)
        self.uuid = uuid
        self.mode = get_mode(mode)

        self.rank_info = get_rank_info(self._hypixel_data)

        with sqlite3.connect('./database/core.db') as conn:
            cursor = conn.cursor()

            cursor.execute(
                "SELECT * FROM historical WHERE uuid = ? and period = ?", (uuid, period))
            historic_data = cursor.fetchone()

            column_names = [desc[0] for desc in cursor.description]
            self.historic_data = dict(zip(column_names, historic_data))

        level = self.historic_data['level']
        self.level = int(level)

        xp_total = xp_from_level(level)
        xp_gained = self.historic_data['Experience']
        stars_gained = level - get_level(xp_total - xp_gained)
        self.stars_gained = f"{rround(stars_gained, 2):,}"

        self.items_purchased = self.historic_data[f'{self.mode}items_purchased_bedwars']
        self.games_played = self.historic_data[f'{self.mode}games_played_bedwars']


    def get_most_played(self):
        solos = self.historic_data['eight_one_games_played_bedwars']
        doubles = self.historic_data['eight_two_games_played_bedwars']
        threes = self.historic_data['four_three_games_played_bedwars']
        fours = self.historic_data['four_four_games_played_bedwars']
        four_vs_vour = self.historic_data['two_four_games_played_bedwars']
        modes_dict = {
            'Solos': solos,
            'Doubles': doubles,
            'Threes':  threes,
            'Fours': fours,
            '4v4': four_vs_vour
        }
        if max(modes_dict.values()) == 0:
            return "N/A"
        return str(max(modes_dict, key=modes_dict.get))


    def _calc_general_stats(self, key_1, key_2):
        val_1 = self.historic_data[key_1]
        val_2 = self.historic_data[key_2]
        ratio = rround(val_1 / (val_2 or 1), 2)
        return f'{val_1:,}', f'{val_2:,}', f'{ratio:,}'


    def get_wins(self):
        return self._calc_general_stats(
            f'{self.mode}wins_bedwars', f'{self.mode}losses_bedwars')


    def get_finals(self):
        return self._calc_general_stats(
            f'{self.mode}final_kills_bedwars', f'{self.mode}final_deaths_bedwars')


    def get_kills(self):
        return self._calc_general_stats(
            f'{self.mode}kills_bedwars', f'{self.mode}deaths_bedwars')


    def get_beds(self):
        return self._calc_general_stats(
            f'{self.mode}beds_broken_bedwars', f'{self.mode}beds_lost_bedwars')


    def get_time_info(self):
        gmt_offset, hour = get_reset_time(self.uuid)

        timezone = f'GMT{prefix_int(gmt_offset)}:00'
        reset_hour = hour_list[hour]

        return timezone, reset_hour
