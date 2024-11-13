from datetime import datetime, UTC

from statalib import SessionManager
from statalib.hypixel import (
    CumulativeStats,
    get_rank_info,
    get_mode,
    rround
)
from statalib.sessions import BedwarsSession


class SessionStats(CumulativeStats):
    def __init__(
        self,
        uuid: str,
        session_info: BedwarsSession,
        hypixel_data: dict,
        mode: str='overall'
    ) -> None:

        super().__init__(hypixel_data, session_info.data, strict_mode=mode)

        self.session = session_info
        session_manager = SessionManager(uuid)
        self.total_sessions = session_manager.session_count()

        self.mode = get_mode(mode)

        self.rank_info = get_rank_info(self._hypixel_data)

        self.level = int(self.level)
        self.stars_gained = f'{rround(self.levels_cum, 2):,}'

        created_at = datetime.fromtimestamp(self.session.creation_timestamp, UTC)
        self.date_started = str(created_at.strftime("%d/%m/%Y"))

        self.winspd, self.finalspd, self.bedspd, self.starspd = self._get_per_day()


    def _get_per_day(self):
        current_time = datetime.now(UTC)
        session_date = datetime.fromtimestamp(self.session.creation_timestamp, UTC)
        days = (current_time - session_date).days

        winspd = rround(self.wins_cum / (days or 1), 2)
        finalspd = rround(self.final_kills_cum / (days or 1), 2)
        bedspd = rround(self.beds_broken_cum / (days or 1), 2)
        starspd = rround(self.levels_cum / (days or 1), 2)

        return f'{winspd:,}', f'{finalspd:,}', f'{bedspd:,}', f'{starspd:,}'
