from dataclasses import dataclass
from typing import Literal, final

from statalib import Mode, ModesEnum
from statalib.fmt import prefix_int
from statalib.hypixel import BedwarsStats, HypixelData, get_rank_info, ratio, rround
from statalib.hypixel.ranks import PlayerRank


@dataclass
class StatDifference:
    value1: int | float
    value2: int | float
    delta: int | float
    symbol: Literal["+", ""]


@final
class CompareStats:
    def __init__(
        self,
        hypixel_data_1: HypixelData,
        hypixel_data_2: HypixelData,
        mode: Mode = ModesEnum.OVERALL.value,
    ) -> None:
        self._bw_1 = BedwarsStats(hypixel_data_1, gamemode=mode)
        self._bw_2 = BedwarsStats(hypixel_data_2, gamemode=mode)

        self.mode = mode

        self.level_1 = int(self._bw_1.level)
        self.level_2 = int(self._bw_2.level)

        self.rank_info_1 = get_rank_info(self._bw_1._hypixel_player_data)
        self.rank_info_2 = get_rank_info(self._bw_2._hypixel_player_data)

        self.wins = StatDifference(
            self._bw_1.wins,
            self._bw_2.wins,
            self._bw_1.wins - self._bw_2.wins,
            "+" if self._bw_1.wins > self._bw_2.wins else "",
        )

        self.losses = StatDifference(
            self._bw_1.losses,
            self._bw_2.losses,
            self._bw_1.losses - self._bw_2.losses,
            "+" if self._bw_1.losses > self._bw_2.losses else "",
        )

        self.wlr = StatDifference(
            ratio(self._bw_1.wins, self._bw_1.losses),
            ratio(self._bw_2.wins, self._bw_2.losses),
            rround(
                ratio(self._bw_1.wins, self._bw_1.losses)
                - ratio(self._bw_2.wins, self._bw_2.losses),
                2,
            ),
            (
                "+"
                if ratio(self._bw_1.wins, self._bw_1.losses)
                > ratio(self._bw_2.wins, self._bw_2.losses)
                else ""
            ),
        )

        self.kills = StatDifference(
            self._bw_1.kills,
            self._bw_2.kills,
            self._bw_1.kills - self._bw_2.kills,
            "+" if self._bw_1.kills > self._bw_2.kills else "",
        )

        self.deaths = StatDifference(
            self._bw_1.deaths,
            self._bw_2.deaths,
            self._bw_1.deaths - self._bw_2.deaths,
            "+" if self._bw_1.deaths > self._bw_2.deaths else "",
        )

        self.kdr = StatDifference(
            ratio(self._bw_1.kills, self._bw_1.deaths),
            ratio(self._bw_2.kills, self._bw_2.deaths),
            rround(
                ratio(self._bw_1.kills, self._bw_1.deaths)
                - ratio(self._bw_2.kills, self._bw_2.deaths),
                2,
            ),
            (
                "+"
                if ratio(self._bw_1.kills, self._bw_1.deaths)
                > ratio(self._bw_2.kills, self._bw_2.deaths)
                else ""
            ),
        )


        self.final_kills = StatDifference(
            self._bw_1.final_kills,
            self._bw_2.final_kills,
            self._bw_1.final_kills - self._bw_2.final_kills,
            "+" if self._bw_1.final_kills > self._bw_2.final_kills else "",
        )

        self.final_deaths = StatDifference(
            self._bw_1.final_deaths,
            self._bw_2.final_deaths,
            self._bw_1.final_deaths - self._bw_2.final_deaths,
            "+" if self._bw_1.final_deaths > self._bw_2.final_deaths else "",
        )

        self.fkdr = StatDifference(
            ratio(self._bw_1.final_kills, self._bw_1.final_deaths),
            ratio(self._bw_2.final_kills, self._bw_2.final_deaths),
            rround(
                ratio(self._bw_1.final_kills, self._bw_1.final_deaths)
                - ratio(self._bw_2.final_kills, self._bw_2.final_deaths),
                2,
            ),
            (
                "+"
                if ratio(self._bw_1.final_kills, self._bw_1.final_deaths)
                > ratio(self._bw_2.final_kills, self._bw_2.final_deaths)
                else ""
            ),
        )


        self.beds_broken = StatDifference(
            self._bw_1.beds_broken,
            self._bw_2.beds_broken,
            self._bw_1.beds_broken - self._bw_2.beds_broken,
            "+" if self._bw_1.beds_broken > self._bw_2.beds_broken else "",
        )

        self.beds_lost = StatDifference(
            self._bw_1.beds_lost,
            self._bw_2.beds_lost,
            self._bw_1.beds_lost - self._bw_2.beds_lost,
            "+" if self._bw_1.beds_lost > self._bw_2.beds_lost else "",
        )

        self.bblr = StatDifference(
            ratio(self._bw_1.beds_broken, self._bw_1.beds_lost),
            ratio(self._bw_2.beds_broken, self._bw_2.beds_lost),
            rround(
                ratio(self._bw_1.beds_broken, self._bw_1.beds_lost)
                - ratio(self._bw_2.beds_broken, self._bw_2.beds_lost),
                2,
            ),
            (
                "+"
                if ratio(self._bw_1.beds_broken, self._bw_1.beds_lost)
                > ratio(self._bw_2.beds_broken, self._bw_2.beds_lost)
                else ""
            ),

        )


        self.wins_comp = f"{self._bw_1.wins:,} / {self._bw_2.wins:,}"
        self.wins_diff = prefix_int(self._bw_1.wins - self._bw_2.wins)

        self.losses_comp = f"{self._bw_1.losses:,} / {self._bw_2.losses:,}"
        self.losses_diff = prefix_int(self._bw_1.losses - self._bw_2.losses)

        wlr_1 = ratio(self._bw_1.wins, self._bw_1.losses)
        wlr_2 = ratio(self._bw_2.wins, self._bw_2.losses)

        self.wlr_comp = f"{wlr_1:,} / {wlr_2:,}"
        self.wlr_diff = prefix_int(rround(wlr_1 - wlr_2, 2))

        self.final_kills_comp = (
            f"{self._bw_1.final_kills:,} / {self._bw_2.final_kills:,}"
        )
        self.final_kills_diff = prefix_int(
            self._bw_1.final_kills - self._bw_2.final_kills
        )

        self.final_deaths_comp = (
            f"{self._bw_1.final_deaths:,} / {self._bw_2.final_deaths:,}"
        )
        self.final_deaths_diff = prefix_int(
            self._bw_1.final_deaths - self._bw_2.final_deaths
        )

        fkdr_1 = ratio(self._bw_1.final_kills, self._bw_1.final_deaths)
        fkdr_2 = ratio(self._bw_2.final_kills, self._bw_2.final_deaths)

        self.fkdr_comp = f"{fkdr_1:,} / {fkdr_2:,}"
        self.fkdr_diff = prefix_int(rround(fkdr_1 - fkdr_2, 2))

        self.beds_broken_comp = (
            f"{self._bw_1.beds_broken:,} / {self._bw_2.beds_broken:,}"
        )
        self.beds_broken_diff = prefix_int(
            self._bw_1.beds_broken - self._bw_2.beds_broken
        )

        self.beds_lost_comp = f"{self._bw_1.beds_lost:,} / {self._bw_2.beds_lost:,}"
        self.beds_lost_diff = prefix_int(self._bw_1.beds_lost - self._bw_2.beds_lost)

        bblr_1 = ratio(self._bw_1.beds_broken, self._bw_1.beds_lost)
        bblr_2 = ratio(self._bw_2.beds_broken, self._bw_2.beds_lost)

        self.bblr_comp = f"{bblr_1:,} / {bblr_2:,}"
        self.bblr_diff = prefix_int(rround(bblr_1 - bblr_2, 2))

        self.kills_comp = f"{self._bw_1.kills:,} / {self._bw_2.kills:,}"
        self.kills_diff = prefix_int(self._bw_1.kills - self._bw_2.kills)

        self.deaths_comp = f"{self._bw_1.deaths:,} / {self._bw_2.deaths:,}"
        self.deaths_diff = prefix_int(self._bw_1.deaths - self._bw_2.deaths)

        kdr_1 = ratio(self._bw_1.kills, self._bw_1.deaths)
        kdr_2 = ratio(self._bw_2.kills, self._bw_2.deaths)

        self.kdr_comp = f"{kdr_1:,} / {kdr_2:,}"
        self.kdr_diff = prefix_int(rround(kdr_1 - kdr_2, 2))

    def get_rank_info_1(self, username: str) -> PlayerRank:
        return self._bw_1.rank_info(username)

    def get_rank_info_2(self, username: str) -> PlayerRank:
        return self._bw_2.rank_info(username)
