import sqlite3

from statalib.historical import get_reset_time
from statalib.functions import prefix_int
from statalib.calctools import (
    CumulativeStats,
    BedwarsStats,
    get_rank_info,
    get_mode,
    rround,
    get_level,
    xp_from_level,
    ratio,
    get_most_mode
)


hour_list = [
    '12:00am', '1:00am', '2:00am', '3:00am', '4:00am', '5:00am', '6:00am',
    '7:00am', '8:00am', '9:00am', '10:00am', '11:00am', '12:00pm',
    '1:00pm', '2:00pm', '3:00pm', '4:00pm', '5:00pm', '6:00pm', '7:00pm',
    '8:00pm', '9:00pm', '10:00pm', '11:00pm'
]


class HistoricalStats(CumulativeStats):
    def __init__(
        self,
        uuid: str,
        identifier: int,
        hypixel_data: dict,
        mode: str='overall'
    ) -> None:
        with sqlite3.connect('./database/core.db') as conn:
            cursor = conn.cursor()

            cursor.execute(
                "SELECT * FROM trackers_new WHERE uuid = ? and tracker = ?",
                (uuid, identifier)
            )
            historic_data = cursor.fetchone()

            column_names = [desc[0] for desc in cursor.description]
            self.historic_data = dict(zip(column_names, historic_data))

        super().__init__(hypixel_data, self.historic_data, strict_mode=mode)

        self.uuid = uuid
        self.mode = get_mode(mode)

        self.stars_gained = f'{rround(self.levels_cum, 2):,}'
        self.level = int(self.level)

        self.rank_info = get_rank_info(self._hypixel_data)

        self.timezone, self.reset_hour = self._get_time_info()


    def _get_time_info(self):
        gmt_offset, hour = get_reset_time(self.uuid)

        timezone = f'GMT{prefix_int(gmt_offset)}:00'
        reset_hour = hour_list[hour]

        return timezone, reset_hour


class LookbackStats(BedwarsStats):
    def __init__(
        self,
        uuid: str,
        period: str,
        hypixel_data: dict,
        mode: str='overall'
    ) -> None:
        super().__init__(hypixel_data, strict_mode=mode)

        with sqlite3.connect('./database/core.db') as conn:
            cursor = conn.cursor()

            cursor.execute(
                "SELECT * FROM historical WHERE uuid = ? and period = ?", (uuid, period))
            historic_data = cursor.fetchone()

            column_names = [desc[0] for desc in cursor.description]
            self.historic_data = dict(zip(column_names, historic_data))

        self.uuid = uuid
        self.mode = get_mode(mode)

        self.rank_info = get_rank_info(self._hypixel_data)

        level = self.historic_data['level']
        self.level = int(level)

        xp_total = xp_from_level(level)
        xp_gained = self.historic_data['Experience']
        stars_gained = level - get_level(xp_total - xp_gained)

        self.stars_gained = f"{rround(stars_gained, 2):,}"

        self.items_purchased_cum = self._get_stat('items_purchased_bedwars')

        self.games_played_cum = self._get_stat('games_played_bedwars')
        self.most_played_cum = self._get_most_played()
        self.timezone, self.reset_hour = self._get_time_info()

        self.wins_cum = self._get_stat('wins_bedwars')
        self.losses_cum = self._get_stat('losses_bedwars')
        self.wlr_cum = ratio(self.wins_cum, self.losses_cum)

        self.final_kills_cum = self._get_stat('final_kills_bedwars')
        self.final_deaths_cum = self._get_stat('final_deaths_bedwars')
        self.fkdr_cum = ratio(self.final_kills_cum, self.final_deaths_cum)

        self.beds_broken_cum = self._get_stat('beds_broken_bedwars')
        self.beds_lost_cum = self._get_stat('beds_lost_bedwars')
        self.bblr_cum = ratio(self.beds_broken_cum, self.beds_lost_cum)

        self.kills_cum = self._get_stat('kills_bedwars')
        self.deaths_cum = self._get_stat('deaths_bedwars')
        self.kdr_cum = ratio(self.kills_cum, self.deaths_cum)


    def _get_stat(self, key: str, default=0):
        return self.historic_data.get(f'{self.mode}{key}', default)


    def _get_most_played(self):
        return get_most_mode(self.historic_data, 'games_played_bedwars')


    def _get_time_info(self):
        gmt_offset, hour = get_reset_time(self.uuid)

        timezone = f'GMT{prefix_int(gmt_offset)}:00'
        reset_hour = hour_list[hour]

        return timezone, reset_hour
