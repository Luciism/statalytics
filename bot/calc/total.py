from statalib.calctools import (
    BedwarsStats,
    get_rank_info,
    get_mode,
    rround,
)


class TotalStats(BedwarsStats):
    def __init__(
        self,
        hypixel_data: dict,
        mode: str='overall'
    ) -> None:
        super().__init__(hypixel_data, strict_mode=mode)

        self.mode = get_mode(mode)
        self.level = int(self.level)
        self.rank_info = get_rank_info(self._hypixel_data)


    def _calc_general_stats(self, key_1, key_2):
        val_1 = self._bedwars_data.get(key_1, 0)
        val_2 = self._bedwars_data.get(key_2, 0)
        ratio = rround(val_1 / (val_2 or 1), 2)
        return f'{val_1:,}', f'{val_2:,}', f'{ratio:,}'


    def get_kills(self):
        return self._calc_general_stats(
            f'{self.mode}kills_bedwars', f'{self.mode}deaths_bedwars')


    def get_finals(self):
        return self._calc_general_stats(
            f'{self.mode}final_kills_bedwars', f'{self.mode}final_deaths_bedwars')


    def get_beds(self):
        return self._calc_general_stats(
            f'{self.mode}beds_broken_bedwars', f'{self.mode}beds_lost_bedwars')


    def get_wins(self):
        return self._calc_general_stats(
            f'{self.mode}wins_bedwars', f'{self.mode}losses_bedwars')


    def get_falling_kills(self):
        return self._calc_general_stats(
            f'{self.mode}fall_kills_bedwars', f'{self.mode}fall_deaths_bedwars')


    def get_void_kills(self):
        return self._calc_general_stats(
            f'{self.mode}void_kills_bedwars', f'{self.mode}void_deaths_bedwars')


    def get_ranged_kills(self):
        return self._calc_general_stats(
            f'{self.mode}projectile_kills_bedwars', f'{self.mode}projectile_deaths_bedwars')


    def get_fire_kills(self):
        return self._calc_general_stats(
            f'{self.mode}fire_tick_kills_bedwars', f'{self.mode}fire_tick_deaths_bedwars')


    def get_misc(self):
        times_voided = self._bedwars_data.get(f'{self.mode}void_deaths_bedwars', 0)
        return f'{self.games_played:,}', f'{times_voided:,}',\
               f'{self.items_purchased:,}', self.winstreak


    def get_misc_pointless(self):
        melee_kills = self._bedwars_data.get(f'{self.mode}entity_attack_kills_bedwars', 0)
        return f'{self.games_played:,}', f'{self.tools_purchased:,}',\
               f'{melee_kills:,}', self.winstreak


    def get_chest_and_coins(self):
        normal = self._bedwars_data.get('bedwars_boxes', 0)
        christmas = self._bedwars_data.get('bedwars_christmas_boxes', 0)
        easter = self._bedwars_data.get('bedwars_easter_boxes', 0)
        halloween = self._bedwars_data.get('bedwars_halloween_boxes', 0)

        total = int(normal + christmas + easter + halloween)
        coins = self._bedwars_data.get('coins', 0)
        return f'{total:,}', f'{coins:,}'
