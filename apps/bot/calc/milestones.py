import math

from statalib.sessions import BedwarsSession
from statalib.hypixel import BedwarsStats, get_rank_info, mode_name_to_id


class MilestonesStats(BedwarsStats):
    def __init__(
        self,
        session_info: BedwarsSession,
        hypixel_data: dict,
        mode: str='overall'
    ) -> None:
        super().__init__(hypixel_data, ganemode=mode)

        self.mode = mode_name_to_id(mode)
        self.session = session_info

        self.level = int(self.level)
        self.rank_info = get_rank_info(self._hypixel_player_data)


    def _calc_general_stats(self, key_1, key_2, ratio):
        # FIXME: im genuinely disappointed in myself for writing this code
        val_1 = self._bedwars_data.get(key_1, 0)
        val_2 = self._bedwars_data.get(key_2, 0)

        if val_1 == 0:
            target_ratio = 1
        elif val_2 > 0:
            target_ratio = math.ceil(val_1 / val_2)
        else:
            target_ratio = int(val_1) + 1

        if val_2 > 1:
            val_1_at_ratio = int(val_2 * target_ratio)
        elif target_ratio > 0:
            val_1_at_ratio = int(val_1 / (target_ratio - 1 or 1) * target_ratio)
        else:
            val_1_at_ratio = 0

        val_1_until_ratio = val_1_at_ratio - val_1

        if self.session is not None:
            session_val_1 = val_1 - self.session.data.__dict__[key_1]
            session_val_2 = val_2 - self.session.data.__dict__[key_2]

            val_1_repitition = val_1_until_ratio / (session_val_1 or 1)

            new_val_2 = session_val_2 * val_1_repitition + val_2

            if new_val_2 > 1:
                val_1_at_ratio = int(new_val_2 * target_ratio)
            elif target_ratio > 0:
                val_1_at_ratio = val_1 / (target_ratio - 1 or 1) * target_ratio
            else:
                val_1_at_ratio = 0

            val_1_until_ratio = val_1_at_ratio - val_1

        target_val_1 = (val_1 // 1000 + 1) * 1000
        val_1_until_val_1 = target_val_1 - val_1

        target_val_2 = (val_2 // 1000 + 1) * 1000
        val_2_until_val_2 = target_val_2 - val_2

        return f"{val_1_until_ratio:,}", f"{val_1_at_ratio:,}",\
               f"{target_ratio:,} {ratio}",f"{val_1_until_val_1:,}",\
                f"{target_val_1:,}", f"{int(val_2_until_val_2):,}", f"{int(target_val_2):,}"


    def get_wins(self):
        return self._calc_general_stats(
            f'{self.mode}wins_bedwars', f'{self.mode}losses_bedwars', 'WLR')


    def get_finals(self):
        return self._calc_general_stats(
            f'{self.mode}final_kills_bedwars', f'{self.mode}final_deaths_bedwars', 'FKDR')


    def get_beds(self):
        return self._calc_general_stats(
            f'{self.mode}beds_broken_bedwars', f'{self.mode}beds_lost_bedwars', 'BBLR')


    def get_kills(self):
        return self._calc_general_stats(
            f'{self.mode}kills_bedwars', f'{self.mode}deaths_bedwars', 'KDR')


    def get_stars(self):
        level_target = (self.level // 100 + 1) * 100
        needed_levels = level_target - self.level
        return needed_levels, level_target
