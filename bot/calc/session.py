import sqlite3
from datetime import datetime

from statalib.calctools import (
    CumulativeStats,
    get_rank_info,
    get_mode,
    rround
)


class SessionStats(CumulativeStats):
    def __init__(
        self,
        uuid: str,
        session: int,
        hypixel_data: dict,
        mode: str='overall'
    ) -> None:
        with sqlite3.connect('./database/core.db') as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM sessions WHERE session=? AND uuid=?", (session, uuid))
            session_data = cursor.fetchone()

            column_names = [desc[0] for desc in cursor.description]
            self.session_data = dict(zip(column_names, session_data))

            cursor.execute(f"SELECT COUNT(*) FROM sessions WHERE uuid = '{uuid}'")
            self.total_sessions = str(cursor.fetchone()[0])

        super().__init__(hypixel_data, self.session_data, strict_mode=mode)

        self.mode = get_mode(mode)

        self.rank_info = get_rank_info(self._hypixel_data)

        self.level = int(self.level)
        self.stars_gained = f'{rround(self.levels_cum, 2):,}'

        old_time = datetime.strptime(self.session_data['date'], "%Y-%m-%d")
        self.date_started = str(old_time.strftime("%d/%m/%Y"))

        self.winspd, self.finalspd, self.bedspd, self.starspd = self._get_per_day()


    def _get_per_day(self):
        current_time = datetime.now()
        session_date = datetime.strptime(self.session_data['date'], "%Y-%m-%d")
        days = (current_time - session_date).days

        winspd = rround(self.wins_cum / (days or 1), 2)
        finalspd = rround(self.final_kills_cum / (days or 1), 2)
        bedspd = rround(self.beds_broken_cum / (days or 1), 2)
        starspd = rround(self.levels_cum / (days or 1), 2)

        return f'{winspd:,}', f'{finalspd:,}', f'{bedspd:,}', f'{starspd:,}'
