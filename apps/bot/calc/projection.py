from typing import final
from statalib import Mode, ModesEnum
from statalib.hypixel import HypixelData, ProjectedStats, get_rank_info
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
            target_level=target,
            gamemode=mode
        )

        self.level = int(self.level)
        self.rank_info = get_rank_info(self._hypixel_player_data)
