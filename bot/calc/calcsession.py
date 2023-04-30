import sqlite3
from datetime import datetime

from calc.calctools import get_progress, get_player_rank_info

class SessionStats:
    def __init__(self, name: str, uuid: str, session: int, mode: str, hypixel_data: dict) -> None:
        self.name = name

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

        self.mode = {"Solos": "eight_one_", "Doubles": "eight_two_", "Threes": "four_three_", "Fours": "four_four_"}.get(mode, "")
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

    def get_wins(self):
        wins = self.hypixel_data_bedwars.get(f'{self.mode}wins_bedwars', 0) - self.session_data[f'{self.mode}wins_bedwars']
        losses = self.hypixel_data_bedwars.get(f'{self.mode}losses_bedwars', 0) - self.session_data[f'{self.mode}losses_bedwars']
        wlr = round(0 if wins == 0 else wins / losses if losses != 0 else wins, 2)
        return f'{wins:,}', f'{losses:,}', f'{wlr:,}'

    def get_finals(self):
        finalkills = self.hypixel_data_bedwars.get(f'{self.mode}final_kills_bedwars', 0) - self.session_data[f'{self.mode}final_kills_bedwars']
        finaldeaths = self.hypixel_data_bedwars.get(f'{self.mode}final_deaths_bedwars', 0) - self.session_data[f'{self.mode}final_deaths_bedwars']
        fkdr = round(0 if finalkills == 0 else finalkills / finaldeaths if finaldeaths != 0 else finalkills, 2)
        return f'{finalkills:,}', f'{finaldeaths:,}', f'{fkdr:,}'

    def get_kills(self):
        kills = self.hypixel_data_bedwars.get(f'{self.mode}kills_bedwars', 0) - self.session_data[f'{self.mode}kills_bedwars']
        deaths = self.hypixel_data_bedwars.get(f'{self.mode}deaths_bedwars', 0) - self.session_data[f'{self.mode}deaths_bedwars']
        kdr = round(0 if kills == 0 else kills / deaths if deaths != 0 else kills, 2)
        return f'{kills:,}', f'{deaths:,}', f'{kdr:,}'

    def get_beds(self):
        bedsbroken = self.hypixel_data_bedwars.get(f'{self.mode}beds_broken_bedwars', 0) - self.session_data[f'{self.mode}beds_broken_bedwars']
        bedslost = self.hypixel_data_bedwars.get(f'{self.mode}beds_lost_bedwars', 0) - self.session_data[f'{self.mode}beds_lost_bedwars']
        bblr = round(0 if bedsbroken == 0 else bedsbroken / bedslost if bedslost != 0 else bedsbroken, 2)
        return f'{bedsbroken:,}', f'{bedslost:,}', f'{bblr:,}'

    def get_per_day(self):
        current_time = datetime.now()
        session_date = datetime.strptime(self.session_data['date'], "%Y-%m-%d")
        days = (current_time - session_date).days

        wins = self.hypixel_data_bedwars.get(f'{self.mode}wins_bedwars', 0) - self.session_data[f'{self.mode}wins_bedwars']
        winspd = round(0 if wins == 0 else wins / days if days != 0 else wins, 2)

        final_kills = self.hypixel_data_bedwars.get(f'{self.mode}final_kills_bedwars', 0) - self.session_data[f'{self.mode}final_kills_bedwars']
        finalspd = round(0 if final_kills == 0 else final_kills / days if days != 0 else final_kills, 2)

        beds_broken = self.hypixel_data_bedwars.get(f'{self.mode}beds_broken_bedwars', 0) - self.session_data[f'{self.mode}beds_broken_bedwars']
        bedspd = round(0 if beds_broken == 0 else beds_broken / days if days != 0 else beds_broken, 2)

        stars_gained = self.hypixel_data.get("achievements", {}).get("bedwars_level", 0) - self.session_data.get('level', 0)
        starspd = round(0 if stars_gained == 0 else stars_gained / days if days != 0 else stars_gained, 2)

        return f'{winspd:,}', f'{finalspd:,}', f'{bedspd:,}', f'{starspd:,}'
