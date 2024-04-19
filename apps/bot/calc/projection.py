from statalib.functions import get_session_data
from statalib.calctools import ProjectedStats, get_rank_info


class PrestigeStats(ProjectedStats):
    def __init__(
        self,
        uuid: str,
        session: int,
        target: int,
        hypixel_data: dict,
        mode: str='overall'
    ) -> None:
        session_data = get_session_data(uuid, session, as_dict=True)

        super().__init__(
            hypixel_data=hypixel_data,
            session_bedwars_data=session_data,
            target_level=target,
            strict_mode=mode
        )

        self.level = int(self.level)
        self.rank_info = get_rank_info(self._hypixel_data)
