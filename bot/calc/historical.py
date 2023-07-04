import sqlite3

from helper.historical import get_reset_time
from helper.calctools import (
    get_progress,
    get_player_rank_info,
    get_mode,
    rround,
    get_level,
    get_player_dict
)


class HistoricalStats:
    def __init__(self, name: str, uuid: str, method: int,
                 mode: str, hypixel_data: dict) -> None:
        self.name, self.uuid = name, uuid
        self.mode = get_mode(mode)

        self.hypixel_data = get_player_dict(hypixel_data)
        self.hypixel_data_bedwars = self.hypixel_data.get('stats', {}).get('Bedwars', {})

        with sqlite3.connect('./database/historical.db') as conn:
            cursor = conn.cursor()

            cursor.execute(f"SELECT * FROM {method} WHERE uuid = '{uuid}'")
            historical_data = cursor.fetchone()

            column_names = [desc[0] for desc in cursor.description]
            self.historical_data = dict(zip(column_names, historical_data))

        level_hypixel = get_level(self.hypixel_data_bedwars.get('Experience', 0))
        level_local = get_level(self.historical_data['Experience'])
        self.level = int(level_hypixel)
        self.stars_gained = f'{rround(level_hypixel - level_local, 2):,}'

        self.items_purchased = (self.hypixel_data_bedwars.get(f'{self.mode}items_purchased_bedwars', 0)
                                - self.historical_data[f'{self.mode}items_purchased_bedwars'])

        self.games_played = (self.hypixel_data_bedwars.get(f'{self.mode}games_played_bedwars', 0)
                             - self.historical_data[f'{self.mode}games_played_bedwars'])

        self.player_rank_info = get_player_rank_info(self.hypixel_data)
        self.progress = get_progress(self.hypixel_data_bedwars)


    def get_most_played(self):
        solos = (self.hypixel_data_bedwars.get('eight_one_games_played_bedwars', 0)
                 - self.historical_data['eight_one_games_played_bedwars'])

        doubles = (self.hypixel_data_bedwars.get('eight_two_games_played_bedwars', 0)
                   - self.historical_data['eight_two_games_played_bedwars'])

        threes = (self.hypixel_data_bedwars.get('four_three_games_played_bedwars', 0)
                  - self.historical_data['four_three_games_played_bedwars'])

        fours = (self.hypixel_data_bedwars.get('four_four_games_played_bedwars', 0)
                 - self.historical_data['four_four_games_played_bedwars'])

        four_vs_four = (self.hypixel_data_bedwars.get('two_four_games_played_bedwars', 0)
                        - self.historical_data['two_four_games_played_bedwars'])

        modes_dict = {
            'Solos': solos,
            'Doubles': doubles,
            'Threes':  threes,
            'Fours': fours,
            '4v4': four_vs_four
        }
        return "N/A" if max(modes_dict.values()) == 0 else str(max(modes_dict, key=modes_dict.get))


    def _calc_general_stats(self, key_1, key_2):
        val_1 = self.hypixel_data_bedwars.get(key_1, 0) - self.historical_data[key_1]
        val_2 = self.hypixel_data_bedwars.get(key_2, 0) - self.historical_data[key_2]
        ratio = rround(val_1 / (val_2 or 1), 2)
        return f'{val_1:,}', f'{val_2:,}', f'{ratio:,}'


    def get_wins(self):
        return self._calc_general_stats(f'{self.mode}wins_bedwars', f'{self.mode}losses_bedwars')


    def get_finals(self):
        return self._calc_general_stats(f'{self.mode}final_kills_bedwars', f'{self.mode}final_deaths_bedwars')


    def get_kills(self):
        return self._calc_general_stats(f'{self.mode}kills_bedwars', f'{self.mode}deaths_bedwars')


    def get_beds(self):
        return self._calc_general_stats(f'{self.mode}beds_broken_bedwars', f'{self.mode}beds_lost_bedwars')


    def get_time_info(self):
        gmt_offset, hour = get_reset_time(self.uuid)

        timezone = f'GMT{"+" if gmt_offset >= 0 else ""}{gmt_offset}:00'
        hours = ['12:00am', '1:00am', '2:00am', '3:00am', '4:00am', '5:00am', '6:00am',
                    '7:00am', '8:00am', '9:00am', '10:00am', '11:00am', '12:00pm', '1:00pm',
                    '2:00pm', '3:00pm', '4:00pm', '5:00pm', '6:00pm', '7:00pm', '8:00pm',
                    '9:00pm', '10:00pm', '11:00pm']
        reset_hour = hours[hour]

        return timezone, reset_hour


class LookbackStats:
    def __init__(self, name: str, uuid: str, table_name: str,
                 mode: str, hypixel_data: dict) -> None:
        self.name, self.uuid, self.table_name = name, uuid, table_name
        self.mode = get_mode(mode)

        self.hypixel_data = get_player_dict(hypixel_data)
        with sqlite3.connect('./database/core.db') as conn:
            cursor = conn.cursor()
            cursor.execute(f"SELECT * FROM linked_accounts WHERE uuid = '{uuid}'")
            linked_data = cursor.fetchone()

        with sqlite3.connect('./database/historical.db') as conn:
            cursor = conn.cursor()
            if linked_data:
                cursor.execute(f"SELECT * FROM configuration WHERE discord_id = '{linked_data[0]}'")
                self.config_data = cursor.fetchone()
            else: self.config_data = ()

            cursor.execute(f"SELECT * FROM {table_name} WHERE uuid = '{uuid}'")
            historical_data = cursor.fetchone()

            column_names = [desc[0] for desc in cursor.description]
            self.historical_data = dict(zip(column_names, historical_data))

        self.level = self.historical_data['level']
        self.stars_gained = f"{rround(get_level(self.historical_data['Experience']), 2):,}"

        self.items_purchased = self.historical_data[f'{self.mode}items_purchased_bedwars']
        self.games_played = self.historical_data[f'{self.mode}games_played_bedwars']
        self.player_rank_info = get_player_rank_info(self.hypixel_data)
        self.progress = get_progress(self.hypixel_data.get('stats', {}).get('Bedwars', {}))


    def get_most_played(self):
        solos = self.historical_data['eight_one_games_played_bedwars']
        doubles = self.historical_data['eight_two_games_played_bedwars']
        threes = self.historical_data['four_three_games_played_bedwars']
        fours = self.historical_data['four_four_games_played_bedwars']
        four_vs_vour = self.historical_data['two_four_games_played_bedwars']
        modes_dict = {
            'Solos': solos,
            'Doubles': doubles,
            'Threes':  threes,
            'Fours': fours,
            '4v4': four_vs_vour
        }
        return "N/A" if max(modes_dict.values()) == 0 else str(max(modes_dict, key=modes_dict.get))


    def _calc_general_stats(self, key_1, key_2):
        val_1 = self.historical_data[key_1]
        val_2 = self.historical_data[key_2]
        ratio = rround(val_1 / (val_2 or 1), 2)
        return f'{val_1:,}', f'{val_2:,}', f'{ratio:,}'


    def get_wins(self):
        return self._calc_general_stats(f'{self.mode}wins_bedwars', f'{self.mode}losses_bedwars')


    def get_finals(self):
        return self._calc_general_stats(f'{self.mode}final_kills_bedwars', f'{self.mode}final_deaths_bedwars')


    def get_kills(self):
        return self._calc_general_stats(f'{self.mode}kills_bedwars', f'{self.mode}deaths_bedwars')


    def get_beds(self):
        return self._calc_general_stats(f'{self.mode}beds_broken_bedwars', f'{self.mode}beds_lost_bedwars')


    def get_time_info(self):
        gmt_offset, hour = get_reset_time(self.uuid)

        timezone = f'GMT{"+" if gmt_offset >= 0 else ""}{gmt_offset}:00'
        hours = ['12:00am', '1:00am', '2:00am', '3:00am', '4:00am', '5:00am', '6:00am',
                    '7:00am', '8:00am', '9:00am', '10:00am', '11:00am', '12:00pm', '1:00pm',
                    '2:00pm', '3:00pm', '4:00pm', '5:00pm', '6:00pm', '7:00pm', '8:00pm',
                    '9:00pm', '10:00pm', '11:00pm']
        reset_hour = hours[hour]

        return timezone, reset_hour