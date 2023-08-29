from datetime import datetime

from statalib.functions import get_session_data
from statalib.calctools import ProjectedStats, get_rank_info


class YearStats(ProjectedStats):
    def __init__(
        self,
        uuid: str,
        session: int,
        year: int,
        hypixel_data: dict,
        mode: str='overall'
    ) -> None:
        session_data = get_session_data(uuid, session, as_dict=True)
        target_date = datetime(year=year, month=1, day=1)

        super().__init__(
            hypixel_data=hypixel_data,
            session_bedwars_data=session_data,
            target_date=target_date,
            strict_mode=mode
        )

        self.rank_info = get_rank_info(self._hypixel_data)
        self.level = int(self.level)
