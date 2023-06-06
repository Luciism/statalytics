from helper.calctools import get_player_rank_info, get_progress,\
                             get_most_played, get_mode, rround, get_level


class Stats:
    def __init__(self, name: str, mode: str, hypixel_data: dict) -> None:
        self.name = name
        self.mode = get_mode(mode)

        self.hypixel_data = hypixel_data.get('player', {})\
                            if hypixel_data.get('player', {}) is not None else {}
        self.hypixel_data_bedwars = self.hypixel_data.get('stats', {}).get('Bedwars', {})

        self.level = int(get_level(self.hypixel_data_bedwars.get('Experience', 0)))
        self.player_rank_info = get_player_rank_info(self.hypixel_data)
        self.progress = get_progress(self.hypixel_data_bedwars)
        self.most_played = get_most_played(self.hypixel_data_bedwars)


    def calc_general_stats(self, key_1, key_2):
        val_1 = self.hypixel_data_bedwars.get(key_1, 0)
        val_2 = self.hypixel_data_bedwars.get(key_2, 0)
        ratio = rround(val_1 / (val_2 or 1), 2)
        return f'{val_1:,}', f'{val_2:,}', f'{ratio:,}'


    def get_kills(self):
        return self.calc_general_stats(
            f'{self.mode}kills_bedwars', f'{self.mode}deaths_bedwars')


    def get_finals(self):
        return self.calc_general_stats(
            f'{self.mode}final_kills_bedwars', f'{self.mode}final_deaths_bedwars')


    def get_beds(self):
        return self.calc_general_stats(
            f'{self.mode}beds_broken_bedwars', f'{self.mode}beds_lost_bedwars')


    def get_wins(self):
        return self.calc_general_stats(
            f'{self.mode}wins_bedwars', f'{self.mode}losses_bedwars')


    def get_falling_kills(self):
        return self.calc_general_stats(
            f'{self.mode}fall_kills_bedwars', f'{self.mode}fall_deaths_bedwars')


    def get_void_kills(self):
        return self.calc_general_stats(
            f'{self.mode}void_kills_bedwars', f'{self.mode}void_deaths_bedwars')


    def get_ranged_kills(self):
        return self.calc_general_stats(
            f'{self.mode}projectile_kills_bedwars', f'{self.mode}projectile_deaths_bedwars')


    def get_fire_kills(self):
        return self.calc_general_stats(
            f'{self.mode}fire_tick_kills_bedwars', f'{self.mode}fire_tick_deaths_bedwars')


    def get_misc(self):
        games_played = self.hypixel_data_bedwars.get(f'{self.mode}games_played_bedwars', 0)
        times_voided = self.hypixel_data_bedwars.get(f'{self.mode}void_deaths_bedwars', 0)
        items_purchased = self.hypixel_data_bedwars.get(f'{self.mode}items_purchased_bedwars', 0)
        winstreak = self.hypixel_data_bedwars.get(f'{self.mode}winstreak')
        winstreak = f'{winstreak:,}' if winstreak is not None else 'API Off'
        return f'{games_played:,}', f'{times_voided:,}', f'{items_purchased:,}', winstreak


    def get_misc_pointless(self):
        games_played = self.hypixel_data_bedwars.get(f'{self.mode}games_played_bedwars', 0)
        tools_purchased = self.hypixel_data_bedwars.get(f'{self.mode}permanent_items_purchased_bedwars', 0)
        melee_kills = self.hypixel_data_bedwars.get(f'{self.mode}entity_attack_kills_bedwars', 0)
        winstreak = self.hypixel_data_bedwars.get(f'{self.mode}winstreak')
        winstreak = f'{winstreak:,}' if winstreak is not None else 'API Off'
        return f'{games_played:,}', f'{tools_purchased:,}', f'{melee_kills:,}', winstreak


    def get_chest_and_coins(self):
        normal = self.hypixel_data_bedwars.get('bedwars_boxes', 0)
        christmas = self.hypixel_data_bedwars.get('bedwars_christmas_boxes', 0)
        easter = self.hypixel_data_bedwars.get('bedwars_easter_boxes', 0)
        halloween = self.hypixel_data_bedwars.get('bedwars_halloween_boxes', 0)

        total = int(normal + christmas + easter + halloween)
        coins = self.hypixel_data_bedwars.get('coins', 0)
        return f'{total:,}', f'{coins:,}'
