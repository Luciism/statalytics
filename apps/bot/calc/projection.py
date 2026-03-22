from typing import final
from statalib.hypixel.projected_stats import TargetLevel
from typing_extensions import override
from statalib import Mode, ModesEnum
from statalib.hypixel import HypixelData, PlayerRank, ProjectedStats, get_rank_info
from statalib.sessions import BedwarsSession


@final
class PrestigeStats(ProjectedStats):
    def __init__(
        self,
        session_info: BedwarsSession,
        target: int,
        hypixel_data: HypixelData,
        mode: Mode=ModesEnum.OVERALL.value
    ) -> None:
        super().__init__(
            hypixel_data=hypixel_data,
            session_info=session_info,
            target=TargetLevel(target),
            gamemode=mode
        )

        self.level = int(self.level)
        self.rank_info = get_rank_info(self._hypixel_player_data)

        self.target: float = target

    def get_rank_info(self, username: str) -> PlayerRank:
        return PlayerRank.from_hypixel_data(username, self._hypixel_player_data)

