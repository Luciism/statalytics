import sqlite3
from datetime import datetime, timedelta

from helper.calctools import (
    get_player_rank_info,
    add_suffixes,
    get_mode,
    rround,
    get_level,
    get_player_dict
)


class ProjectedStats:
    def __init__(self, name: str, uuid: str, session: int,
                 mode: str, target: int, hypixel_data: dict) -> None:
        self.name = name
        self.target = target
        self.mode = get_mode(mode)

        self.hypixel_data = get_player_dict(hypixel_data)
        self.hypixel_data_bedwars = self.hypixel_data.get('stats', {}).get('Bedwars', {})

        with sqlite3.connect('./database/core.db') as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM sessions WHERE session=? AND uuid=?", (session, uuid))
            session_data = cursor.fetchone()
            column_names = [desc[0] for desc in cursor.description]
            self.session_data = dict(zip(column_names, session_data))

        self.level_local =  get_level(self.session_data['Experience'])  # how many levels player had when they started session
        self.level_hypixel = get_level(self.hypixel_data_bedwars.get('Experience', 0))  # current hypixel level
        self.levels_to_go = self.target - self.level_hypixel  # levels to target
        self.stars_to_go = add_suffixes(int(self.target - int(self.level_hypixel)))[0]

        self.levels_gained = self.level_hypixel - self.level_local  # how many levels gained during session
        if self.levels_gained == 0:
            self.levels_gained = 0.0001

        self.level_repetition = self.levels_to_go / self.levels_gained  # how many times they have to gain the session amount of levels to get to the goal
        self.complete_percent = f"{round((self.level_hypixel / self.target) * 100, 2)}%"
        self.player_rank_info = get_player_rank_info(self.hypixel_data)


    def _get_increase_factor(self, value):
        increase_factor = 0
        if self.level_repetition > 0:
            try:
                increase_factor = 1 / (self.level_repetition ** self.level_repetition)  # add some extra for skill progression
            except OverflowError:
                pass

        increased_value = round(float(value) + (increase_factor * value))
        return increased_value


    def _get_trajectory(self, value_1, value_2):
        value_1_hypixel = self.hypixel_data_bedwars.get(value_1, 0)
        value_2_hypixel = self.hypixel_data_bedwars.get(value_2, 0)

        value_1_local = value_1_hypixel - self.session_data[value_1]
        value_2_local = value_2_hypixel - self.session_data[value_2]

        value_1_repetition = value_1_local * self.level_repetition
        value_2_repetition = value_2_local * self.level_repetition

        projected_value_1 = self._get_increase_factor(value_1_repetition) + value_1_hypixel
        projected_value_2 = round(value_2_repetition + value_2_hypixel)
        projected_ratio = rround(projected_value_1 / (projected_value_2 or 1), 2)

        return projected_value_1, projected_value_2, projected_ratio


    def get_kills(self):
        self.kills = self._get_trajectory(
            value_1=f'{self.mode}kills_bedwars', value_2=f'{self.mode}deaths_bedwars')

        formatted_values = add_suffixes(*self.kills)
        return formatted_values


    def get_finals(self):
        self.finals = self._get_trajectory(
            value_1=f'{self.mode}final_kills_bedwars', value_2=f'{self.mode}final_deaths_bedwars')

        formatted_values = add_suffixes(*self.finals)
        return formatted_values


    def get_beds(self):
        self.beds = self._get_trajectory(
            value_1=f'{self.mode}beds_broken_bedwars', value_2=f'{self.mode}beds_lost_bedwars')

        formatted_values = add_suffixes(*self.beds)
        return formatted_values


    def get_wins(self):
        self.wins = self._get_trajectory(
            value_1=f'{self.mode}wins_bedwars', value_2=f'{self.mode}losses_bedwars')

        formatted_values = add_suffixes(*self.wins)
        return formatted_values


    def get_per_star(self):
        avg_wins = (self.wins[0] - self.hypixel_data_bedwars.get(
            f'{self.mode}wins_bedwars', 0)) / self.levels_to_go

        avg_finals = (self.finals[0] - self.hypixel_data_bedwars.get(
            f'{self.mode}final_kills_bedwars', 0)) / self.levels_to_go

        avg_beds = (self.beds[0] - self.hypixel_data_bedwars.get(
            f'{self.mode}beds_broken_bedwars', 0)) / self.levels_to_go

        return str(rround(avg_wins, 2)), str(rround(avg_finals, 2)), str(rround(avg_beds, 2))


    def get_stars_per_day(self):
        current_time = datetime.now()
        old_time = datetime.strptime(self.session_data['date'], "%Y-%m-%d")
        days = (current_time - old_time).days
        if days == 0:
            days = 1
        return str(rround(self.levels_gained / days if self.levels_gained != 0 else 0, 2))


    def get_projection_date(self):
        current_time = datetime.now()
        old_time = datetime.strptime(self.session_data['date'], "%Y-%m-%d")
        try:
            days = (current_time - old_time).days
            if days == 0:
                days = 1

            daystogo = int((0 if self.levels_gained == 0 else days / self.levels_gained) * self.levels_to_go)
            future_date = current_time + timedelta(days=daystogo)
            return str(future_date.strftime("%b %d, %Y"))
        except OverflowError:
            return "Deceased"


    def get_items_purchased(self):
        items_hypixel = self.hypixel_data_bedwars.get(f'{self.mode}items_purchased_bedwars', 0)
        items_local = items_hypixel - self.session_data[f'{self.mode}items_purchased_bedwars']

        items_repetition = items_local * self.level_repetition
        projected_items = items_repetition + items_hypixel

        items_purchased = add_suffixes(round(projected_items))
        return items_purchased[0]
