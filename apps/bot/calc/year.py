from datetime import UTC, datetime

from statalib import BedwarsSession, calctools


class YearStats(calctools.ProjectedStats):
    def __init__(
        self,
        uuid: str,
        session_info: BedwarsSession,
        year: int,
        hypixel_data: dict,
        mode: str='overall'
    ) -> None:
        target_date = datetime(year=year, month=1, day=1, tzinfo=UTC)

        super().__init__(
            hypixel_data=hypixel_data,
            session_info=session_info,
            target_date=target_date,
            strict_mode=mode
        )

        self.rank_info = calctools.get_rank_info(self._hypixel_data)
        self.level = int(self.level)
