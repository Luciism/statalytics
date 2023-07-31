import sqlite3
from datetime import datetime

from statalib.calctools import (
    BedwarsStats,
    get_rank_info,
    add_suffixes,
    get_mode,
    get_level,
    rround
)


class YearStats(BedwarsStats):
    def __init__(
        self,
        uuid: str,
        session: int,
        year: int,
        hypixel_data: dict,
        mode: str='overall'
    ) -> None:
        super().__init__(hypixel_data, strict_mode=mode)

        self.mode = get_mode(mode)

        with sqlite3.connect('./database/core.db') as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM sessions WHERE session=? AND uuid=?", (session, uuid))
            session_data = cursor.fetchone()
            column_names = [desc[0] for desc in cursor.description]
            self.session_data = dict(zip(column_names, session_data))

        self.current_time = datetime.now().date()
        old_time = datetime.strptime(self.session_data['date'], "%Y-%m-%d").date()

        if not year:
            year = self.current_time.year + 1

        self.days = (self.current_time - old_time).days
        self.days_to_go = (datetime(year, 1, 1).date() - self.current_time).days
        if self.days == 0:
            self.days = 1

        if self.days_to_go == 0:
            self.days_to_go = 1

        self.level_local = get_level(self.session_data['Experience'])
        self.level_hypixel = self.level
        self.levels_gained = max(self.level_hypixel - self.level_local, 0.0001)

        self.stars_per_day = self.levels_gained / self.days
        self.projected_star = int(self.stars_per_day * self.days_to_go + self.level_hypixel)
        self.levels_to_go = self.projected_star - self.level_hypixel

        if self.levels_to_go == 0:
            self.levels_to_go = 0.0001

        self.level_repetition = self.levels_to_go / self.levels_gained

        self.rank_info = get_rank_info(self._hypixel_data)

        years_to_go = year - datetime.now().year
        
        complete_percentage = round(
            ((365 * years_to_go) - int(self.days_to_go)) / (365 * years_to_go) * 100, 2)

        self.complete_percentage = f'{complete_percentage}%'


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


    def _get_average(self, value: str):
        value_hypixel = self._bedwars_data.get(value, 0)  # current value on hypixel
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
        self.wins_data = self._get_trajectory(
            value_1=f'{self.mode}wins_bedwars',
            value_2=f'{self.mode}losses_bedwars')
        return add_suffixes(*self.wins_data)


    def get_finals(self):
        self.finals_data = self._get_trajectory(
            value_1=f'{self.mode}final_kills_bedwars',
            value_2=f'{self.mode}final_deaths_bedwars')
        return add_suffixes(*self.finals_data)


    def get_beds(self):
        self.beds_data = self._get_trajectory(
            value_1=f'{self.mode}beds_broken_bedwars',
            value_2=f'{self.mode}beds_lost_bedwars')
        return add_suffixes(*self.beds_data)


    def get_kills(self):
        self.kills_data = self._get_trajectory(
            value_1=f'{self.mode}kills_bedwars',
            value_2=f'{self.mode}deaths_bedwars')
        return add_suffixes(*self.kills_data)


    def get_per_star(self):
        avg_wins = (self.wins_data[0] - self.wins) / self.levels_to_go

        avg_finals = (self.finals_data[0] - self.final_kills) / self.levels_to_go

        avg_beds = (self.beds_data[0] - self.beds_broken) / self.levels_to_go

        return str(rround(avg_wins, 2)).replace('-', ''),\
               str(rround(avg_finals, 2)).replace('-', ''),\
               str(rround(avg_beds, 2)).replace('-', '')


    def get_items_purchased(self):
        items_avg, items_hypixel = self._get_average(
            value=f'{self.mode}items_purchased_bedwars')
        projected_items = self.days_to_go * items_avg + items_hypixel

        items_purchased = add_suffixes(round(projected_items))
        return items_purchased[0]


    def get_target(self):
        stars_to_go = self.stars_per_day * self.days_to_go
        return int(stars_to_go + self.level_hypixel)
