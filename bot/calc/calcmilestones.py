import math
import sqlite3

from calc.calctools import get_player_rank_info

class Stats:
    def __init__(self, name: str, uuid: str, mode: str, session: int, hypixel_data: dict) -> None:
        self.name = name

        with sqlite3.connect('./database/sessions.db') as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM sessions WHERE session=? AND uuid=?", (session, uuid))
            session_data = cursor.fetchone()
            if session_data:
                column_names = [desc[0] for desc in cursor.description]
                self.session_data = dict(zip(column_names, session_data))
            else:
                self.session_data = None

        self.hypixel_data = hypixel_data.get('player', {}) if hypixel_data.get('player', {}) != None else {}
        self.hypixel_data_bedwars = self.hypixel_data.get('stats', {}).get('Bedwars', {})

        self.level = self.hypixel_data.get("achievements", {}).get("bedwars_level", 0)

        self.mode = {"Solos": "eight_one_", "Doubles": "eight_two_", "Threes": "four_three_", "Fours": "four_four_"}.get(mode, "")

        self.player_rank_info = get_player_rank_info(self.hypixel_data)

    def get_wins(self):
        wins = self.hypixel_data_bedwars.get(f'{self.mode}wins_bedwars', 0)
        losses = self.hypixel_data_bedwars.get(f'{self.mode}losses_bedwars', 0)

        # WLR milestones
        target_wlr = math.ceil(0 if wins == 0 else wins / losses if losses != 0 else wins+1)
        wins_at_wlr = int(losses * target_wlr if losses > 1 else ((wins / (target_wlr - 1) if target_wlr > 0 else 0) * target_wlr))
        wins_until_wlr = wins_at_wlr - wins

        if self.session_data:
            session_wins = wins - self.session_data[f'{self.mode}wins_bedwars']
            session_losses = losses - self.session_data[f'{self.mode}losses_bedwars']

            wins_repitition = 0 if wins_until_wlr == 0 else wins_until_wlr / session_wins if session_wins != 0 else wins_until_wlr
            new_losses = session_losses * wins_repitition + losses

            wins_at_wlr = int(new_losses * target_wlr if new_losses > 1 else ((wins / (target_wlr - 1) if target_wlr > 0 else 0) * target_wlr))
            wins_until_wlr = wins_at_wlr - wins

        # Wins target milestone
        target_wins = (wins // 1000 + 1) * 1000
        wins_until_wins = target_wins - wins

        # Losses not so much target milestone
        target_losses = (losses // 1000 + 1) * 1000
        losses_until_losses = target_losses - losses

        return f"{wins_until_wlr:,}", f"{wins_at_wlr:,}", f"{target_wlr:,} WLR", f"{wins_until_wins:,}", f"{target_wins:,}", f"{int(losses_until_losses):,}", f"{int(target_losses):,}"

    def get_finals(self):
        final_kills = self.hypixel_data_bedwars.get(f'{self.mode}final_kills_bedwars', 0)
        final_deaths = self.hypixel_data_bedwars.get(f'{self.mode}final_deaths_bedwars', 0)

        target_fkdr = math.ceil(0 if final_kills == 0 else final_kills / final_deaths if final_deaths != 0 else final_kills+1)
        final_kills_at_fkdr = int(final_deaths * target_fkdr if final_deaths > 1 else ((final_kills / (target_fkdr - 1) if target_fkdr > 0 else 0) * target_fkdr))
        final_kills_until_fkdr = final_kills_at_fkdr - final_kills

        if self.session_data:
            session_final_kills = final_kills - self.session_data[f'{self.mode}final_kills_bedwars']
            session_final_deaths = final_deaths - self.session_data[f'{self.mode}final_deaths_bedwars']

            final_kills_repitition = 0 if final_kills_until_fkdr == 0 else final_kills_until_fkdr / session_final_kills if session_final_kills != 0 else final_kills_until_fkdr
            new_final_deaths = session_final_deaths * final_kills_repitition + final_deaths

            final_kills_at_fkdr = int(new_final_deaths * target_fkdr if new_final_deaths > 1 else ((final_kills / (target_fkdr - 1) if target_fkdr > 0 else 0) * target_fkdr))
            final_kills_until_fkdr = final_kills_at_fkdr - final_kills

        target_final_kills = (final_kills // 1000 + 1) * 1000
        final_kills_until_final_kills = target_final_kills - final_kills

        target_final_deaths = (final_deaths // 1000 + 1) * 1000
        final_deaths_until_final_deaths = target_final_deaths - final_deaths

        return f"{final_kills_until_fkdr:,}", f"{final_kills_at_fkdr:,}", f"{target_fkdr:,} FKDR", f"{final_kills_until_final_kills:,}", f"{target_final_kills:,}", f"{int(final_deaths_until_final_deaths):,}", f"{int(target_final_deaths):,}"

    def get_beds(self):
        beds_broken = self.hypixel_data_bedwars.get(f'{self.mode}beds_broken_bedwars', 0)
        beds_lost = self.hypixel_data_bedwars.get(f'{self.mode}beds_lost_bedwars', 0)

        target_bblr = math.ceil(0 if beds_broken == 0 else beds_broken / beds_lost if beds_lost != 0 else beds_broken+1)
        beds_broken_at_bblr = int(beds_lost * target_bblr if beds_lost > 1 else ((beds_broken / (target_bblr - 1) if target_bblr > 0 else 0) * target_bblr))
        beds_broken_until_bblr = beds_broken_at_bblr - beds_broken

        if self.session_data:
            session_beds_broken = beds_broken - self.session_data[f'{self.mode}beds_broken_bedwars']
            session_beds_lost = beds_lost - self.session_data[f'{self.mode}beds_lost_bedwars']

            beds_broken_repitition = 0 if beds_broken_until_bblr == 0 else beds_broken_until_bblr / session_beds_broken if session_beds_broken != 0 else beds_broken_until_bblr
            new_beds_lost = session_beds_lost * beds_broken_repitition + beds_lost

            beds_broken_at_bblr = int(new_beds_lost * target_bblr if new_beds_lost > 1 else ((beds_broken / (target_bblr - 1) if target_bblr > 0 else 0) * target_bblr))
            beds_broken_until_bblr = beds_broken_at_bblr - beds_broken

        target_beds_broken = (beds_broken // 1000 + 1) * 1000
        beds_broken_until_beds_broken = target_beds_broken - beds_broken

        target_beds_lost = (beds_lost // 1000 + 1) * 1000
        beds_lost_until_beds_lost = target_beds_lost - beds_lost

        return f"{beds_broken_until_bblr:,}", f"{beds_broken_at_bblr:,}", f"{target_bblr:,} BBLR", f"{beds_broken_until_beds_broken:,}", f"{target_beds_broken:,}", f"{int(beds_lost_until_beds_lost):,}", f"{int(target_beds_lost):,}"

    def get_kills(self):
        kills = self.hypixel_data_bedwars.get(f'{self.mode}kills_bedwars', 0)
        deaths = self.hypixel_data_bedwars.get(f'{self.mode}deaths_bedwars', 0)
        
        target_kdr = math.ceil(0 if kills == 0 else kills / deaths if deaths != 0 else kills+1)
        kills_at_kdr = int(deaths * target_kdr if deaths > 1 else ((kills / (target_kdr - 1) if target_kdr > 0 else 0) * target_kdr))
        kills_until_kdr = kills_at_kdr - kills

        if self.session_data:
            session_kills = kills - self.session_data[f'{self.mode}kills_bedwars']
            session_deaths = deaths - self.session_data[f'{self.mode}deaths_bedwars']

            kills_repitition = 0 if kills_until_kdr == 0 else kills_until_kdr / session_kills if session_kills != 0 else kills_until_kdr
            new_deaths = session_deaths * kills_repitition + deaths

            kills_at_kdr = int(new_deaths * target_kdr if new_deaths > 1 else ((kills / (target_kdr - 1) if target_kdr > 0 else 0) * target_kdr))
            kills_until_kdr = kills_at_kdr - kills

        target_kills = (kills // 1000 + 1) * 1000
        kills_until_kills = target_kills - kills

        target_deaths = (deaths // 1000 + 1) * 1000
        deaths_until_deaths = target_deaths - deaths

        return f"{kills_until_kdr:,}", f"{kills_at_kdr:,}", f"{target_kdr:,} KDR", f"{kills_until_kills:,}", f"{target_kills:,}", f"{int(deaths_until_deaths):,}", f"{int(target_deaths):,}"

    def get_stars(self):
        level_target = (self.level // 100 + 1) * 100
        needed_levels = level_target - self.level
        return str(needed_levels), str(level_target)