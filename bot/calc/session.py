import sqlite3
from datetime import datetime

from helper.calctools import get_progress, get_player_rank_info, get_mode, rround

class SessionStats:
    def __init__(self, name: str, uuid: str, session: int, mode: str, hypixel_data: dict) -> None:
        self.name = name
        self.mode = get_mode(mode)

        self.hypixel_data = hypixel_data.get('player', {}) if hypixel_data.get('player', {}) is not None else {}
        self.hypixel_data_bedwars = self.hypixel_data.get('stats', {}).get('Bedwars', {})

        with sqlite3.connect('./database/sessions.db') as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM sessions WHERE session=? AND uuid=?", (session, uuid))
            session_data = cursor.fetchone()

            column_names = [desc[0] for desc in cursor.description]
            self.session_data = dict(zip(column_names, session_data))

            cursor.execute(f"SELECT COUNT(*) FROM sessions WHERE uuid = '{uuid}'")
            self.total_sessions = str(cursor.fetchone()[0])

        self.level = self.hypixel_data.get('achievements', {}).get('bedwars_level', 0)
        self.stars_gained = str(self.level - self.session_data['level'])

        old_time = datetime.strptime(self.session_data['date'], "%Y-%m-%d")
        self.date_started = str(old_time.strftime("%d/%m/%Y"))

        self.games_played = str(self.hypixel_data_bedwars.get(f'{self.mode}games_played_bedwars', 0) - self.session_data[f'{self.mode}games_played_bedwars'])
        self.player_rank_info = get_player_rank_info(self.hypixel_data)
        self.progress = get_progress(self.hypixel_data_bedwars)

    def get_most_played(self):
        solos = self.hypixel_data_bedwars.get('eight_one_games_played_bedwars', 0) - self.session_data['eight_one_games_played_bedwars']
        doubles = self.hypixel_data_bedwars.get('eight_two_games_played_bedwars', 0) - self.session_data['eight_two_games_played_bedwars']
        threes = self.hypixel_data_bedwars.get('four_three_games_played_bedwars', 0) - self.session_data['four_three_games_played_bedwars']
        fours =  self.hypixel_data_bedwars.get('four_four_games_played_bedwars', 0) - self.session_data['four_four_games_played_bedwars']
        findgreatest = {
            'Solos': solos,
            'Doubles': doubles,
            'Threes':  threes,
            'Fours': fours
        }
        return "N/A" if max(findgreatest.values()) == 0 else str(max(findgreatest, key=findgreatest.get))

    def calc_general_stats(self, key_1, key_2):
        val_1 = self.hypixel_data_bedwars.get(key_1, 0) - self.session_data[key_1]
        val_2 = self.hypixel_data_bedwars.get(key_2, 0) - self.session_data[key_2]
        ratio = rround(val_1 / (val_2 or 1), 2)
        return f'{val_1:,}', f'{val_2:,}', f'{ratio:,}'

    def get_wins(self):
        return self.calc_general_stats(f'{self.mode}wins_bedwars', f'{self.mode}losses_bedwars')

    def get_finals(self):
        return self.calc_general_stats(f'{self.mode}final_kills_bedwars', f'{self.mode}final_deaths_bedwars')

    def get_kills(self):
        return self.calc_general_stats(f'{self.mode}kills_bedwars', f'{self.mode}deaths_bedwars')

    def get_beds(self):
        return self.calc_general_stats(f'{self.mode}beds_broken_bedwars', f'{self.mode}beds_lost_bedwars')

    def get_per_day(self):
        current_time = datetime.now()
        session_date = datetime.strptime(self.session_data['date'], "%Y-%m-%d")
        days = (current_time - session_date).days

        wins = self.hypixel_data_bedwars.get(f'{self.mode}wins_bedwars', 0) - self.session_data[f'{self.mode}wins_bedwars']
        winspd = rround(0 if wins == 0 else wins / days if days != 0 else wins, 2)

        final_kills = self.hypixel_data_bedwars.get(f'{self.mode}final_kills_bedwars', 0) - self.session_data[f'{self.mode}final_kills_bedwars']
        finalspd = rround(final_kills / (days or 1), 2)

        beds_broken = self.hypixel_data_bedwars.get(f'{self.mode}beds_broken_bedwars', 0) - self.session_data[f'{self.mode}beds_broken_bedwars']
        bedspd = rround(beds_broken / (days or 1), 2)

        stars_gained = self.hypixel_data.get("achievements", {}).get("bedwars_level", 0) - self.session_data.get('level', 0)
        starspd = rround(stars_gained / (days or 1), 2)

        return f'{winspd:,}', f'{finalspd:,}', f'{bedspd:,}', f'{starspd:,}'
