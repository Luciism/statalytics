from typing import final
from statalib import ModesEnum, hypixel


@final
class WinstreakStats(hypixel.BedwarsStats):
    def __init__(
        self,
        hypixel_data: hypixel.HypixelData
    ) -> None:
        super().__init__(hypixel_data, gamemode=ModesEnum.OVERALL.value)

        self.rank_info = hypixel.get_rank_info(self._hypixel_player_data)
        self.level = int(self.level)

        self.winstreak_overall: str = self.__format_ws('winstreak')
        self.winstreak_solos: str = self.__format_ws('eight_one_winstreak')
        self.winstreak_doubles: str = self.__format_ws('eight_two_winstreak')
        self.winstreak_threes: str = self.__format_ws('four_three_winstreak')
        self.winstreak_fours: str = self.__format_ws('four_four_winstreak')
        self.winstreak_4v4: str = self.__format_ws('two_four_winstreak')

        # True if winstreak is present, False in all other cases
        winstreak_overall: int = self._bedwars_data.get('winstreak')
        self.api_status = "On" if winstreak_overall is not None else "Off"


    def __format_ws(self, key: str) -> str:
        value = self._bedwars_data.get(key)

        if value is None:
            return 'N/A'

        return f'{value:,}'
