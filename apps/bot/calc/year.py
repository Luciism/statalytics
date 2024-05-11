from datetime import datetime

from statalib import SessionManager
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
        session_info = SessionManager(uuid).get_session(session)
        target_date = datetime(year=year, month=1, day=1)

        super().__init__(
            hypixel_data=hypixel_data,
            session_info=session_info,
            target_date=target_date,
            strict_mode=mode
        )

        self.rank_info = get_rank_info(self._hypixel_data)
        self.level = int(self.level)
