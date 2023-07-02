import sqlite3
from datetime import datetime

from helper.calctools import (
    get_player_rank_info,
    add_suffixes,
    get_mode,
    get_level,
    rround,
    get_player_dict
)


class YearStats:
    def __init__(self, name: str, uuid: str, session: int,
                 year: int, mode: str, hypixel_data: dict) -> None:
        self.name = name
        self.mode = get_mode(mode)

        self.hypixel_data = get_player_dict(hypixel_data)
        self.hypixel_data_bedwars = self.hypixel_data.get('stats', {}).get('Bedwars', {})

        with sqlite3.connect('./database/sessions.db') as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM sessions WHERE session=? AND uuid=?", (session, uuid))
            session_data = cursor.fetchone()
            column_names = [desc[0] for desc in cursor.description]
            self.session_data = dict(zip(column_names, session_data))

        self.current_time = datetime.now().date()
        old_time = datetime.strptime(self.session_data['date'], "%Y-%m-%d").date()

        if not year: year = self.current_time.year + 1
        self.days = (self.current_time - old_time).days
        self.days_to_go = (datetime(year, 1, 1).date() - self.current_time).days
        if self.days == 0: self.days = 1
        if self.days_to_go == 0: self.days_to_go = 1

        self.level_local = get_level(self.session_data['Experience'])  # how many levels player had when they started session
        self.level_hypixel = get_level(self.hypixel_data_bedwars.get('Experience', 0))  # current hypixel level
        self.levels_gained = self.level_hypixel - self.level_local  # how many levels gained during session
        if self.levels_gained == 0: self.levels_gained = 0.0001
        self.stars_per_day = self.levels_gained / self.days
        self.projected_star = int(self.stars_per_day * self.days_to_go + self.level_hypixel)
        self.levels_to_go = self.projected_star - self.level_hypixel
        if self.levels_to_go == 0: self.levels_to_go = 0.0001
        self.level_repetition = self.levels_to_go / self.levels_gained

        self.player_rank_info = get_player_rank_info(self.hypixel_data)


    def _get_increase_factor(self, value):
        if self.level_repetition > 0:
            try: increase_factor = 1 / (self.level_repetition ** self.level_repetition)  # add some extra for skill progression
            except OverflowError: increase_factor = 0
        else: increase_factor = 0

        increased_value = round(float(value) + (increase_factor * value))
        return increased_value


    def _get_average(self, value: str):
        value_hypixel = self.hypixel_data_bedwars.get(value, 0)  # current value on hypixel
        value_session = value_hypixel - self.session_data[value]  # total value player gained during session
        return value_session / self.levels_gained, value_hypixel


    def _get_trajectory(self, value_1: str, value_2: str):
        value_1_per_star, value_1_hypixel = self._get_average(value_1)
        value_2_per_star, value_2_hypixel = self._get_average(value_2)

        projected_value_1 = self.levels_to_go * value_1_per_star  # avg per star * days to go + current value
        projected_value_1 = self._get_increase_factor(projected_value_1) + value_1_hypixel
        projected_value_2 = self.levels_to_go * value_2_per_star + value_2_hypixel

        projected_ratio = rround(projected_value_1 / (projected_value_2 or 1), 2)

        return int(projected_value_1), int(projected_value_2), rround(projected_ratio, 2)


    def get_wins(self):
        self.wins = self._get_trajectory(
            value_1=f'{self.mode}wins_bedwars', value_2=f'{self.mode}losses_bedwars')
        return add_suffixes(*self.wins)


    def get_finals(self):
        self.finals = self._get_trajectory(
            value_1=f'{self.mode}final_kills_bedwars', value_2=f'{self.mode}final_deaths_bedwars')
        return add_suffixes(*self.finals)


    def get_beds(self):
        self.beds = self._get_trajectory(
            value_1=f'{self.mode}beds_broken_bedwars', value_2=f'{self.mode}beds_lost_bedwars')
        return add_suffixes(*self.beds)


    def get_kills(self):
        self.kills = self._get_trajectory(
            value_1=f'{self.mode}kills_bedwars', value_2=f'{self.mode}deaths_bedwars')
        return add_suffixes(*self.kills)


    def get_per_star(self):
        avg_wins = (self.wins[0] - self.hypixel_data_bedwars.get(
            f'{self.mode}wins_bedwars', 0)) / self.levels_to_go

        avg_finals = (self.finals[0] - self.hypixel_data_bedwars.get(
            f'{self.mode}final_kills_bedwars', 0)) / self.levels_to_go

        avg_beds = (self.beds[0] - self.hypixel_data_bedwars.get(
            f'{self.mode}beds_broken_bedwars', 0)) / self.levels_to_go

        return str(rround(avg_wins, 2)).replace('-', ''),\
            str(rround(avg_finals, 2)).replace('-', ''), str(rround(avg_beds, 2)).replace('-', '')


    def get_items_purchased(self):
        items_avg, items_hypixel = self._get_average(value=f'{self.mode}items_purchased_bedwars')
        projected_items = self.days_to_go * items_avg + items_hypixel

        items_purchased = add_suffixes(round(projected_items))
        return items_purchased[0]


    def get_target(self):
        stars_to_go = self.stars_per_day * self.days_to_go
        return int(stars_to_go + self.level_hypixel)
