import sqlite3
from datetime import datetime, timedelta

from statalib.calctools import (
    BedwarsStats,
    get_rank_info,
    add_suffixes,
    get_mode,
    rround,
    get_level,
)


class ProjectedStats(BedwarsStats):
    def __init__(
        self,
        uuid: str,
        session: int,
        target: int,
        hypixel_data: dict,
        mode: str='overall'
    ) -> None:
        super().__init__(hypixel_data, strict_mode=mode)

        self.target = target
        self.mode = get_mode(mode)

        with sqlite3.connect('./database/core.db') as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM sessions WHERE session=? AND uuid=?", (session, uuid))
            session_data = cursor.fetchone()
            column_names = [desc[0] for desc in cursor.description]
            self.session_data = dict(zip(column_names, session_data))

        # how many levels player had when they started session
        self.level_local = get_level(self.session_data['Experience'])

        self.level_hypixel = self.level
        self.levels_to_go = self.target - self.level_hypixel

        # formatted
        self.stars_to_go = add_suffixes(int(self.target - int(self.level_hypixel)))[0]

        self.levels_gained = max(self.level_hypixel - self.level_local, 0.0001)

        # how many times they have to gain the session amount of levels to get to the goal
        self.level_repetition = self.levels_to_go / self.levels_gained
        self.complete_percent = f"{round((self.level_hypixel / self.target) * 100, 2)}%"
        self.rank_info = get_rank_info(self._hypixel_data)


    def _get_increase_factor(self, value):
        increase_factor = 0
        if self.level_repetition > 0:
            try:
                # add some extra for skill progression
                increase_factor = 1 / (self.level_repetition ** self.level_repetition)
            except OverflowError:
                pass

        increased_value = round(float(value) + (increase_factor * value))
        return increased_value


    def _get_trajectory(self, value_1, value_2):
        value_1_hypixel = self._bedwars_data.get(value_1, 0)
        value_2_hypixel = self._bedwars_data.get(value_2, 0)

        value_1_local = value_1_hypixel - self.session_data[value_1]
        value_2_local = value_2_hypixel - self.session_data[value_2]

        value_1_repetition = value_1_local * self.level_repetition
        value_2_repetition = value_2_local * self.level_repetition

        projected_value_1 = self._get_increase_factor(value_1_repetition) + value_1_hypixel
        projected_value_2 = round(value_2_repetition + value_2_hypixel)
        projected_ratio = rround(projected_value_1 / (projected_value_2 or 1), 2)

        return projected_value_1, projected_value_2, projected_ratio


    def get_kills(self):
        self.kills_data = self._get_trajectory(
            value_1=f'{self.mode}kills_bedwars', value_2=f'{self.mode}deaths_bedwars')

        formatted_values = add_suffixes(*self.kills_data)
        return formatted_values


    def get_finals(self):
        self.finals_data = self._get_trajectory(
            value_1=f'{self.mode}final_kills_bedwars', value_2=f'{self.mode}final_deaths_bedwars')

        formatted_values = add_suffixes(*self.finals_data)
        return formatted_values


    def get_beds(self):
        self.beds_data = self._get_trajectory(
            value_1=f'{self.mode}beds_broken_bedwars', value_2=f'{self.mode}beds_lost_bedwars')

        formatted_values = add_suffixes(*self.beds_data)
        return formatted_values


    def get_wins(self):
        self.wins_data = self._get_trajectory(
            value_1=f'{self.mode}wins_bedwars', value_2=f'{self.mode}losses_bedwars')

        formatted_values = add_suffixes(*self.wins_data)
        return formatted_values


    def get_per_star(self):
        avg_wins = (self.wins_data[0] - self.wins) / self.levels_to_go

        avg_finals = (self.finals_data[0] - self.final_kills) / self.levels_to_go

        avg_beds = (self.beds_data[0] - self.beds_broken) / self.levels_to_go

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

            if self.levels_gained == 0:
                days_to_go = 0
            else:
                days_to_go = int((days / self.levels_gained) * self.levels_to_go)

            future_date = current_time + timedelta(days=days_to_go)
            return str(future_date.strftime("%b %d, %Y"))
        except OverflowError:
            return "Deceased"


    def get_items_purchased(self):
        items_local = (self.items_purchased -
            self.session_data[f'{self.mode}items_purchased_bedwars'])

        items_repetition = items_local * self.level_repetition
        projected_items = items_repetition + self.items_purchased

        items_purchased = add_suffixes(round(projected_items))
        return items_purchased[0]
