import os
import sqlite3
from datetime import datetime, timedelta

class SessionStats:
    def __init__(self, name: str, uuid: str, session: int, mode: str, target: int, hypixel_data: dict) -> None:
        self.name = name
        self.target = target
        self.mode = mode

        self.hypixel_data = hypixel_data.get('player', {}) if hypixel_data.get('player', {}) is not None else {}
        self.hypixel_data_bedwars = self.hypixel_data.get('stats', {}).get('Bedwars', {})

        with sqlite3.connect('./database/sessions.db') as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM sessions WHERE session=? AND uuid=?", (session, uuid))
            session_data = cursor.fetchone()
            column_names = [desc[0] for desc in cursor.description]
            self.session_data = dict(zip(column_names, session_data))

        level_local =  self.session_data['level'] # how many levels player had when they started session
        self.level_hypixel = self.hypixel_data.get("achievements", {}).get("bedwars_level", 0) # current hypixel level
        self.levels_to_go = self.target - self.hypixel_data.get("achievements", {}).get("bedwars_level", 0) # levels to target

        self.levelsgained = self.level_hypixel - level_local # how many levels gained during session
        if self.levelsgained == 0:
            expdif = self.hypixel_data_bedwars.get('Experience', 0) - self.session_data['Experience']
            self.levelsgained = expdif / 5000

        self.levelrepitition = self.levels_to_go / self.levelsgained if self.levelsgained != 0 else 0 # how many times they have to gain the session amount of levels to get to the goal

        self.mode = {"Solos": "eight_one_", "Doubles": "eight_two_", "Threes": "four_three_", "Fours": "four_four_"}.get(mode, "")
        self.suffixes = {
            10**60: 'NoDc', 10**57: 'OcDc', 10**54: 'SpDc', 10**51: 'SxDc', 10**48: 'QiDc', 10**45: 'QaDc',
            10**42: 'TDc', 10**39: 'DDc', 10**36: 'UDc', 10**33: 'Dc', 10**30: 'No', 10**27: 'Oc', 10**24: 'Sp',
            10**21: 'Sx', 10**18: 'Qi', 10**15: 'Qa', 10**12: 'T', 10**9: 'B', 10**6: 'M'
        }
        self.complete_percent = f"{round((self.level_hypixel / self.target) * 100, 2)}%"

    def get_player_rank_info(self):
        rank_info = {
            'rank': self.hypixel_data.get('rank', 'NONE') if self.name != "Technoblade" else "TECHNO",
            'packageRank': self.hypixel_data.get('packageRank', 'NONE'),
            'newPackageRank': self.hypixel_data.get('newPackageRank', 'NONE'),
            'monthlyPackageRank': self.hypixel_data.get('monthlyPackageRank', 'NONE'),
            'rankPlusColor': self.hypixel_data.get('rankPlusColor', None) if self.name != "Technoblade" else "AQUA"
        }
        return rank_info

    def get_kills(self):
        kills_hypixel = self.hypixel_data_bedwars.get(f'{self.mode}kills_bedwars', 0) # current kills on hypixel
        deaths_hypixel = self.hypixel_data_bedwars.get(f'{self.mode}deaths_bedwars', 0) # current deaths on hypixel

        kills_local = kills_hypixel - self.session_data[f'{self.mode}kills_bedwars'] # how many kills the player has gotten during the session
        deaths_local = deaths_hypixel - self.session_data[f'{self.mode}deaths_bedwars'] # how many deaths the player has gotten during the session

        kills_repitition = kills_local * self.levelrepitition # how many kills they need by multiplied by the amount of session star count sums they need to get to the goal
        deaths_repitition = deaths_local * self.levelrepitition # same thing as kills but for deaths

        projected_kills = kills_repitition + kills_hypixel # total kills to get to goal added with the kills they already have
        projected_deaths = deaths_repitition + deaths_hypixel # same thing as kills but for deaths

        if self.levelrepitition > 0:
            increase_factor = (int(projected_kills / (self.levelrepitition * 100)) * 0.1) * (int(self.levelrepitition / 20) * 0.1) # add some extra for skill progression
            projected_kills = round(float(projected_kills) + (increase_factor * projected_kills))

            increase_factor = (int(projected_deaths / (self.levelrepitition * 100)) * 0.1) * (int(self.levelrepitition / 20) * 0.1)
            projected_deaths = round(float(projected_deaths) + (increase_factor * projected_deaths))

        projected_kdr = round(0 if projected_kills == 0 else projected_kills / projected_deaths if projected_deaths != 0 else projected_kills, 2) # get kdr

        formatted_values = []
        for value in (projected_kills, projected_deaths, projected_kdr):
            for num, suffix in self.suffixes.items():
                if value >= num:
                    value = f"{value/num:,.1f}{suffix}"
                    break
            else:
                value = f"{value:,}"
            formatted_values.append(value)
        return formatted_values

    def get_finals(self):
        final_kills_hypixel = self.hypixel_data_bedwars.get(f'{self.mode}final_kills_bedwars', 0)
        final_deaths_hypixel = self.hypixel_data_bedwars.get(f'{self.mode}final_deaths_bedwars', 0)

        final_kills_local = final_kills_hypixel - self.session_data[f'{self.mode}final_kills_bedwars']
        final_deaths_local = final_deaths_hypixel - self.session_data[f'{self.mode}final_deaths_bedwars']

        final_kills_repitition = final_kills_local * self.levelrepitition
        final_deaths_repitition = final_deaths_local * self.levelrepitition

        projected_final_kills = final_kills_repitition + final_kills_hypixel
        projected_final_deaths = final_deaths_repitition + final_deaths_hypixel

        if self.levelrepitition > 0:
            increase_factor = (int(projected_final_kills / (self.levelrepitition * 100)) * 0.1) * (int(self.levelrepitition / 20) * 0.1)
            projected_final_kills = round(float(projected_final_kills) + (increase_factor * projected_final_kills))

            increase_factor = (int(projected_final_deaths / (self.levelrepitition * 100)) * 0.1) * (int(self.levelrepitition / 20) * 0.1)
            projected_final_deaths = round(float(projected_final_deaths) + (increase_factor * projected_final_deaths))

        projected_fkdr = round(0 if projected_final_kills == 0 else projected_final_kills / projected_final_deaths if projected_final_deaths != 0 else projected_final_kills, 2)

        formatted_values = []
        for value in (projected_final_kills, projected_final_deaths, projected_fkdr):
            for num, suffix in self.suffixes.items():
                if value >= num:
                    value = f"{value/num:,.1f}{suffix}"
                    break
            else:
                value = f"{value:,}"
            formatted_values.append(value)
        return formatted_values

    def get_beds(self):
        beds_broken_hypixel = self.hypixel_data_bedwars.get(f'{self.mode}beds_broken_bedwars', 0)
        beds_lost_hypixel = self.hypixel_data_bedwars.get(f'{self.mode}beds_lost_bedwars', 0)

        beds_broken_local = beds_broken_hypixel - self.session_data[f'{self.mode}beds_broken_bedwars']
        beds_lost_local = beds_lost_hypixel - self.session_data[f'{self.mode}beds_lost_bedwars']

        beds_broken_repitition = beds_broken_local * self.levelrepitition
        beds_lost_repitition = beds_lost_local * self.levelrepitition

        projected_beds_broken = beds_broken_repitition + beds_broken_hypixel
        projected_beds_lost = beds_lost_repitition + beds_lost_hypixel

        if self.levelrepitition > 0:
            increase_factor = (int(projected_beds_broken / (self.levelrepitition * 100)) * 0.1) * (int(self.levelrepitition / 20) * 0.1)
            projected_beds_broken = round(float(projected_beds_broken) + (increase_factor * projected_beds_broken))

            increase_factor = (int(projected_beds_lost / (self.levelrepitition * 100)) * 0.1) * (int(self.levelrepitition / 20) * 0.1)
            projected_beds_lost = round(float(projected_beds_lost) + (increase_factor * projected_beds_lost))

        projected_bblr = round(0 if projected_beds_broken == 0 else projected_beds_broken / projected_beds_lost if projected_beds_lost != 0 else projected_beds_broken, 2)

        formatted_values = []
        for value in (projected_beds_broken, projected_beds_lost, projected_bblr):
            for num, suffix in self.suffixes.items():
                if value >= num:
                    value = f"{value/num:,.1f}{suffix}"
                    break
            else:
                value = f"{value:,}"
            formatted_values.append(value)
        return formatted_values

    def get_wins(self):
        wins_hypixel = self.hypixel_data_bedwars.get(f'{self.mode}wins_bedwars', 0)
        losses_hypixel = self.hypixel_data_bedwars.get(f'{self.mode}losses_bedwars', 0)

        wins_local = wins_hypixel - self.session_data[f'{self.mode}wins_bedwars']
        losses_local = losses_hypixel - self.session_data[f'{self.mode}losses_bedwars']

        wins_repitition = wins_local * self.levelrepitition
        losses_repitition = losses_local * self.levelrepitition

        projected_wins = wins_repitition + wins_hypixel
        projected_losses = losses_repitition + losses_hypixel

        if self.levelrepitition > 0:
            increase_factor = (int(projected_wins / (self.levelrepitition * 100)) * 0.1) * (int(self.levelrepitition / 20) * 0.1)
            projected_wins = round(float(projected_wins) + (increase_factor * projected_wins))

            increase_factor = (int(projected_losses / (self.levelrepitition * 100)) * 0.1) * (int(self.levelrepitition / 20) * 0.1)
            projected_losses = round(float(projected_losses) + (increase_factor * projected_losses))

        projected_wlr = round(0 if projected_wins == 0 else projected_wins / projected_losses if projected_losses != 0 else projected_wins, 2)

        formatted_values = []
        for value in (projected_wins, projected_losses, projected_wlr):
            for num, suffix in self.suffixes.items():
                if value >= num:
                    value = f"{value/num:,.1f}{suffix}"
                    break
            else:
                value = f"{value:,}"
            formatted_values.append(value)
        return formatted_values

    def get_per_star(self):
        session_wins = self.hypixel_data_bedwars.get(f'{self.mode}wins_bedwars', 0) - self.session_data[f'{self.mode}wins_bedwars']
        session_final_kills = self.hypixel_data_bedwars.get(f'{self.mode}final_kills_bedwars', 0) - self.session_data[f'{self.mode}final_kills_bedwars']
        session_beds_broken = self.hypixel_data_bedwars.get(f'{self.mode}beds_broken_bedwars', 0) - self.session_data[f'{self.mode}beds_broken_bedwars']

        wins_repitition = session_wins * self.levelrepitition
        final_kills_repitition = session_final_kills * self.levelrepitition
        beds_broken_repitition = session_beds_broken * self.levelrepitition
        return str(round(wins_repitition / self.levels_to_go, 2)), str(round(final_kills_repitition / self.levels_to_go, 2)), str(round(beds_broken_repitition / self.levels_to_go, 2))

    def get_stars_per_day(self):
        current_time = datetime.now()
        old_time = datetime.strptime(self.session_data['date'], "%Y-%m-%d")
        days = (current_time - old_time).days
        days = 1 if days == 0 else days
        return str(round(self.levelsgained / days if self.levelsgained != 0 else 0, 2))

    def get_projection_date(self):
        current_time = datetime.now()
        old_time = datetime.strptime(self.session_data['date'], "%Y-%m-%d")
        try:
            days = (current_time - old_time).days
            days = 1 if days == 0 else days

            daystogo = int((0 if self.levelsgained == 0 else days / self.levelsgained) * self.levels_to_go)
            future_date = current_time + timedelta(days=daystogo)
            return str(future_date.strftime("%b %d, %Y"))
        except OverflowError:
            return "Deceased"

    def get_level_to_go(self):
        levels_to_go = self.target - self.level_hypixel
        for num, suffix in self.suffixes.items():
            if levels_to_go >= num:
                levels_to_go = f"{levels_to_go/num:,.1f}{suffix}"
                break
        else:
            levels_to_go = f"{levels_to_go:,}"
        return levels_to_go

    def get_items_purchased(self):
        items_purchased = self.hypixel_data_bedwars.get(f'{self.mode}items_purchased_bedwars', 0)
        items_purchased_per_star = items_purchased / self.level_hypixel
        projected_items_purchased = self.target * items_purchased_per_star
        for num, suffix in self.suffixes.items():
            if projected_items_purchased >= num:
                projected_items_purchased = f"{projected_items_purchased/num:,.1f}{suffix}"
                break
        else:
            projected_items_purchased = f"{round(projected_items_purchased):,}"
        return projected_items_purchased

    def get_formatted_stars_to_go(self):
        stars_to_go = self.levels_to_go
        for num, suffix in self.suffixes.items():
            if stars_to_go >= num:
                stars_to_go = f"{stars_to_go/num:,.1f}{suffix}"
                break
        else:
            stars_to_go = f"{stars_to_go:,}"
        return stars_to_go
