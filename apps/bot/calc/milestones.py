from dataclasses import dataclass
from typing import final

from statalib import Mode, ModesEnum
from statalib.sessions import BedwarsSession
from statalib.hypixel import BedwarsStats, HypixelData, PlayerRank, get_rank_info 


@dataclass
class Milestone:
    target_ratio: float
    target_value: int
    value_at_ratio: int
    x_until_target_value: int
    x_until_target_ratio: int


@final
class MilestonesStats(BedwarsStats):
    def __init__(
        self,
        session_info: BedwarsSession | None,
        hypixel_data: HypixelData,
        mode: Mode=ModesEnum.OVERALL.value 
    ) -> None:
        super().__init__(hypixel_data, gamemode=mode)

        self.mode = mode
        self.session = session_info

        self.level = int(self.level)
        self.rank_info = get_rank_info(self._hypixel_player_data)

        self.target_level = (self.level // 100 + 1) * 100
        self.levels_until_target = self.target_level - self.level


    def _calc_milestone(self, key_good: str, key_bad: str) -> Milestone:
        value_good: int = self._bedwars_data.get(key_good, 0)
        value_bad: int = self._bedwars_data.get(key_bad, 0)
        current_ratio = value_good / (value_bad or 1)

        target_ratio = int(value_good / (value_bad or 1)) + 1
        target_value = int(value_good / 1000 + 1) * 1000

        value_at_ratio = round(value_good * target_ratio / current_ratio)

        if self.session is not None:
            session_good: int = value_good - self.session.data.__dict__[key_good]
            session_bad: int = value_bad - self.session.data.__dict__[key_bad]
            session_ratio = (session_good or 1) / (session_bad or 1)

            if session_good or session_bad:
                d = (target_ratio * value_bad - value_good) / ((session_ratio - target_ratio) or 1)
                value_at_ratio = round(value_good + session_ratio * d)
                # value_bad_at_ratio = value_bad + d


        x_until_target_value = target_value - value_good
        x_until_target_ratio = value_at_ratio - value_good

        return Milestone(
            target_ratio=target_ratio,
            target_value=target_value,
            value_at_ratio=value_at_ratio,
            x_until_target_value=x_until_target_value,
            x_until_target_ratio=x_until_target_ratio
        )

    def get_rank_info(self, username: str) -> PlayerRank:
        return PlayerRank.from_hypixel_data(username, self.hypixel_player_data)

    def get_wins(self):
        return self._calc_milestone(
            f'{self.mode.prefix}wins_bedwars', f'{self.mode.prefix}losses_bedwars')


    def get_finals(self):
        return self._calc_milestone(
            f'{self.mode.prefix}final_kills_bedwars', f'{self.mode.prefix}final_deaths_bedwars')


    def get_beds(self):
        return self._calc_milestone(
            f'{self.mode.prefix}beds_broken_bedwars', f'{self.mode.prefix}beds_lost_bedwars')


    def get_kills(self):
        return self._calc_milestone(
            f'{self.mode.prefix}kills_bedwars', f'{self.mode.prefix}deaths_bedwars')


    def get_stars(self):
        level_target = (self.level // 100 + 1) * 100
        needed_levels = level_target - self.level
        return needed_levels, level_target
