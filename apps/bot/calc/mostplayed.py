from typing import final
from statalib import ModesEnum
from statalib.hypixel import (
    BedwarsStats,
    HypixelData,
    PlayerRank,
)


@final
class MostPlayedStats(BedwarsStats):
    def __init__(
        self,
        hypixel_data: HypixelData,
    ) -> None:
        super().__init__(hypixel_data, gamemode=ModesEnum.OVERALL.value)

        solos: int = self._bedwars_data.get('eight_one_games_played_bedwars', 0)
        doubles: int = self._bedwars_data.get('eight_two_games_played_bedwars', 0)
        threes: int = self._bedwars_data.get('four_three_games_played_bedwars', 0)
        fours: int = self._bedwars_data.get('four_four_games_played_bedwars', 0)

        # Get ratio
        values: list[int] = [solos, doubles, threes, fours]
        normal = 1 / (sum(values) or 1)

        MAX_BAR_HEIGHT = 100  # %
        heights = [normal * value * MAX_BAR_HEIGHT for value in values]

        # Make sure highest bar always reaches top
        height_multiplier = MAX_BAR_HEIGHT / (max(heights) or 1)

        self.solos_bar_height = min(max(heights[0] * height_multiplier, 0), 100)
        self.doubles_bar_height = min(max(heights[1] * height_multiplier, 0), 100)
        self.threes_bar_height = min(max(heights[2] * height_multiplier, 0), 100)
        self.fours_bar_height = min(max(heights[3] * height_multiplier, 0), 100)



    def get_rank_info(self, username: str) -> PlayerRank:
        return PlayerRank.from_hypixel_data(username, self.hypixel_player_data)
