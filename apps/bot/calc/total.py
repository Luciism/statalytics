from typing import final
from statalib import Mode, ModesEnum
from statalib.hypixel import (
    BedwarsStats,
    HypixelData,
    get_rank_info,
    rround,
)


@final
class TotalStats(BedwarsStats):
    def __init__(
        self,
        hypixel_data: HypixelData,
        mode: Mode=ModesEnum.OVERALL.value
    ) -> None:
        super().__init__(hypixel_data, gamemode=mode)

        self.mode = mode
        self.level = int(self.level)
        self.rank_info = get_rank_info(self._hypixel_player_data)

        self.falling_kills = self._get_mode_stats('fall_kills_bedwars')
        self.falling_deaths = self._get_mode_stats('fall_deaths_bedwars')
        self.falling_kdr = rround(self.falling_kills / (self.falling_deaths or 1), 2)

        self.void_kills = self._get_mode_stats('void_kills_bedwars')
        self.void_deaths = self._get_mode_stats('void_deaths_bedwars')
        self.void_kdr = rround(self.void_kills / (self.void_deaths or 1), 2)

        self.fire_kills = self._get_mode_stats('fire_tick_kills_bedwars')
        self.fire_deaths = self._get_mode_stats('fire_tick_deaths_bedwars')
        self.fire_kdr = rround(self.fire_kills / (self.fire_deaths or 1), 2)

        self.projectile_kills = self._get_mode_stats('projectile_kills_bedwars')
        self.projectile_deaths = self._get_mode_stats('projectile_deaths_bedwars')
        self.projectile_kdr = rround(
            self.projectile_kills / (self.projectile_deaths or 1), 2)

        self.melee_kills = self._get_mode_stats('entity_attack_kills_bedwars')
