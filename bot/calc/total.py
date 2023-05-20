from calc.calctools import get_player_rank_info, get_progress, get_most_played, get_mode

class Stats:
    def __init__(self, name: str, mode: str, hypixel_data: dict) -> None:
        self.name = name
        self.mode = get_mode(mode)

        self.hypixel_data = hypixel_data.get('player', {}) if hypixel_data.get('player', {}) is not None else {}
        self.hypixel_data_bedwars = self.hypixel_data.get('stats', {}).get('Bedwars', {})

        self.level = self.hypixel_data.get("achievements", {}).get("bedwars_level", 0)
        self.player_rank_info = get_player_rank_info(self.hypixel_data)
        self.progress = get_progress(self.hypixel_data_bedwars)
        self.most_played = get_most_played(self.hypixel_data_bedwars)

    def get_kills(self):
        kills = self.hypixel_data_bedwars.get(f'{self.mode}kills_bedwars', 0)
        deaths = self.hypixel_data_bedwars.get(f'{self.mode}deaths_bedwars', 0)
        kdr = round(0 if kills == 0 else kills / deaths if deaths != 0 else kills, 2)
        return f'{kills:,}', f'{deaths:,}', f'{kdr:,}'

    def get_finals(self):
        final_kills = self.hypixel_data_bedwars.get(f'{self.mode}final_kills_bedwars', 0)
        final_deaths = self.hypixel_data_bedwars.get(f'{self.mode}final_deaths_bedwars', 0)
        fkdr = round(0 if final_kills == 0 else final_kills / final_deaths if final_deaths != 0 else final_kills, 2)
        return f'{final_kills:,}', f'{final_deaths:,}', f'{fkdr:,}'

    def get_beds(self):
        beds_broken = self.hypixel_data_bedwars.get(f'{self.mode}beds_broken_bedwars', 0)
        beds_lost = self.hypixel_data_bedwars.get(f'{self.mode}beds_lost_bedwars', 0)
        bblr = round(0 if beds_broken == 0 else beds_broken / beds_lost if beds_lost != 0 else beds_broken, 2)
        return f'{beds_broken:,}', f'{beds_lost:,}', f'{bblr:,}'

    def get_wins(self):
        wins = self.hypixel_data_bedwars.get(f'{self.mode}wins_bedwars', 0)
        losses = self.hypixel_data_bedwars.get(f'{self.mode}losses_bedwars', 0)
        wlr = round(0 if wins == 0 else wins / losses if losses != 0 else wins, 2)
        return f'{wins:,}', f'{losses:,}', f'{wlr:,}'

    def get_misc(self):
        games_played = self.hypixel_data_bedwars.get(f'{self.mode}games_played_bedwars', 0)
        times_voided = self.hypixel_data_bedwars.get(f'{self.mode}void_deaths_bedwars', 0)
        items_purchased = self.hypixel_data_bedwars.get(f'{self.mode}items_purchased_bedwars', 0)
        winstreak = self.hypixel_data_bedwars.get(f'{self.mode}winstreak', 0)
        return f'{games_played:,}', f'{times_voided:,}', f'{items_purchased:,}', f'{winstreak:,}'

    def get_chest_and_coins(self):
        normal = self.hypixel_data_bedwars.get('bedwars_boxes', 0)
        christmas = self.hypixel_data_bedwars.get('bedwars_christmas_boxes', 0)
        easter = self.hypixel_data_bedwars.get('bedwars_easter_boxes', 0)
        halloween = self.hypixel_data_bedwars.get('bedwars_halloween_boxes', 0)

        total = int(normal + christmas + easter + halloween)
        coins = self.hypixel_data_bedwars.get('coins', 0)
        return f'{total:,}', f'{coins:,}'

    def get_falling_kills(self):
        fall_kills = self.hypixel_data_bedwars.get(f'{self.mode}fall_kills_bedwars', 0)
        fall_deaths = self.hypixel_data_bedwars.get(f'{self.mode}fall_deaths_bedwars', 0)
        fall_kdr = round(0 if fall_kills == 0 else fall_kills / fall_deaths if fall_deaths != 0 else fall_kills, 2)
        return f'{fall_kills:,}', f'{fall_deaths:,}', f'{fall_kdr:,}'

    def get_void_kills(self):
        void_kills = self.hypixel_data_bedwars.get(f'{self.mode}void_kills_bedwars', 0)
        void_deaths = self.hypixel_data_bedwars.get(f'{self.mode}void_deaths_bedwars', 0)
        void_kdr = round(0 if void_kills == 0 else void_kills / void_deaths if void_deaths != 0 else void_kills, 2)
        return f'{void_kills:,}', f'{void_deaths:,}', f'{void_kdr:,}'

    def get_ranged_kills(self):
        ranged_kills = self.hypixel_data_bedwars.get(f'{self.mode}projectile_kills_bedwars', 0)
        ranged_deaths = self.hypixel_data_bedwars.get(f'{self.mode}projectile_deaths_bedwars', 0)
        ranged_kdr = round(0 if ranged_kills == 0 else ranged_kills / ranged_deaths if ranged_deaths != 0 else ranged_kills, 2)
        return f'{ranged_kills:,}', f'{ranged_deaths:,}', f'{ranged_kdr:,}'

    def get_fire_kills(self):
        fire_kills = self.hypixel_data_bedwars.get(f'{self.mode}fire_tick_kills_bedwars', 0)
        fire_deaths = self.hypixel_data_bedwars.get(f'{self.mode}fire_tick_deaths_bedwars', 0)
        fire_kdr = round(0 if fire_kills == 0 else fire_kills / fire_deaths if fire_deaths != 0 else fire_kills, 2)
        return f'{fire_kills:,}', f'{fire_deaths:,}', f'{fire_kdr:,}'

    def get_misc_pointless(self):
        games_played = self.hypixel_data_bedwars.get(f'{self.mode}games_played_bedwars', 0)
        tools_purchased = self.hypixel_data_bedwars.get(f'{self.mode}permanent_items_purchased_bedwars', 0)
        melee_kills = self.hypixel_data_bedwars.get(f'{self.mode}entity_attack_kills_bedwars', 0)
        winstreak = self.hypixel_data_bedwars.get(f'{self.mode}winstreak', 0)
        return f'{games_played:,}', f'{tools_purchased:,}', f'{melee_kills:,}', f'{winstreak:,}'
