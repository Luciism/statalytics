from datetime import UTC, datetime
from typing import final

from statalib import Mode, ModesEnum, hypixel, sessions


@final
class YearStats(hypixel.ProjectedStats):
    def __init__(
        self,
        uuid: str,
        session_info: sessions.BedwarsSession,
        year: int,
        hypixel_data: hypixel.HypixelData,
        mode: Mode=ModesEnum.OVERALL.value
    ) -> None:
        target_date = datetime(year=year, month=1, day=1, tzinfo=UTC)

        super().__init__(
            hypixel_data=hypixel_data,
            session_info=session_info,
            target_date=target_date,
            gamemode=mode
        )

        self.rank_info = hypixel.get_rank_info(self._hypixel_player_data)
        self.level = int(self.level)
