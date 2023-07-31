import sqlite3
from datetime import datetime

from statalib.calctools import (
    BedwarsStats,
    get_rank_info,
    get_mode,
    rround
)


class SessionStats(BedwarsStats):
    def __init__(
        self,
        uuid: str,
        session: int,
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

            cursor.execute(f"SELECT COUNT(*) FROM sessions WHERE uuid = '{uuid}'")
            self.total_sessions = str(cursor.fetchone()[0])

        self.level = int(self.level)
        self.stars_gained = str(self.level - self.session_data['level'])

        old_time = datetime.strptime(self.session_data['date'], "%Y-%m-%d")
        self.date_started = str(old_time.strftime("%d/%m/%Y"))

        self.games_played = str(self.games_played - 
            self.session_data[f'{self.mode}games_played_bedwars'])

        self.rank_info = get_rank_info(self._hypixel_data)


    def get_most_played(self):
        solos = (self._bedwars_data.get('eight_one_games_played_bedwars', 0)
                 - self.session_data['eight_one_games_played_bedwars'])

        doubles = (self._bedwars_data.get('eight_two_games_played_bedwars', 0)
                   - self.session_data['eight_two_games_played_bedwars'])

        threes = (self._bedwars_data.get('four_three_games_played_bedwars', 0)
                  - self.session_data['four_three_games_played_bedwars'])

        fours =  (self._bedwars_data.get('four_four_games_played_bedwars', 0)
                  - self.session_data['four_four_games_played_bedwars'])

        four_vs_four = (self._bedwars_data.get('two_four_games_played_bedwars', 0)
                         - self.session_data['two_four_games_played_bedwars'])

        modes_dict = {
            'Solos': solos,
            'Doubles': doubles,
            'Threes':  threes,
            'Fours': fours,
            '4v4': four_vs_four
        }
        return "N/A" if max(modes_dict.values()) == 0\
            else str(max(modes_dict, key=modes_dict.get))


    def _calc_general_stats(self, key_1, key_2):
        val_1 = self._bedwars_data.get(key_1, 0) - self.session_data[key_1]
        val_2 = self._bedwars_data.get(key_2, 0) - self.session_data[key_2]
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


    def get_per_day(self):
        current_time = datetime.now()
        session_date = datetime.strptime(self.session_data['date'], "%Y-%m-%d")
        days = (current_time - session_date).days

        wins = (self.wins - self.session_data[f'{self.mode}wins_bedwars'])
        winspd = rround(wins / (days or 1), 2)

        final_kills = (self.final_kills -
            self.session_data[f'{self.mode}final_kills_bedwars'])
        finalspd = rround(final_kills / (days or 1), 2)

        beds_broken = (self.beds_broken -
            self.session_data[f'{self.mode}beds_broken_bedwars'])
        bedspd = rround(beds_broken / (days or 1), 2)

        stars_gained = (self.level - self.session_data.get('level', 0))
        starspd = rround(stars_gained / (days or 1), 2)

        return f'{winspd:,}', f'{finalspd:,}', f'{bedspd:,}', f'{starspd:,}'
