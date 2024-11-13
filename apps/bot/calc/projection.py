from statalib.hypixel import ProjectedStats, get_rank_info
from statalib.sessions import BedwarsSession


class PrestigeStats(ProjectedStats):
    def __init__(
        self,
        session_info: BedwarsSession,
        target: int,
        hypixel_data: dict,
        mode: str='overall'
    ) -> None:
        super().__init__(
            hypixel_data=hypixel_data,
            session_info=session_info,
            target_level=target,
            strict_mode=mode
        )

        self.level = int(self.level)
        self.rank_info = get_rank_info(self._hypixel_data)
