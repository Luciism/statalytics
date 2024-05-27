import statalib
from statalib import calctools
from statalib import rotational_stats as rotational


HOUR_LIST = [
    '12:00am', '1:00am', '2:00am', '3:00am', '4:00am', '5:00am', '6:00am',
    '7:00am', '8:00am', '9:00am', '10:00am', '11:00am', '12:00pm',
    '1:00pm', '2:00pm', '3:00pm', '4:00pm', '5:00pm', '6:00pm', '7:00pm',
    '8:00pm', '9:00pm', '10:00pm', '11:00pm'
]


class RotationalStats(calctools.CumulativeStats):
    def __init__(
        self,
        uuid: str,
        rotation_type: rotational.RotationType,
        hypixel_data: dict,
        mode: str='overall'
    ) -> None:
        self.rotational_data = rotational.RotationalStatsManager(uuid) \
            .get_rotational_data(rotation_type)

        super().__init__(hypixel_data, self.rotational_data.data, strict_mode=mode)

        self.uuid = uuid
        self.mode = calctools.get_mode(mode)

        self.stars_gained = f'{calctools.rround(self.levels_cum, 2):,}'
        self.level = int(self.level)

        self.rank_info = calctools.get_rank_info(self._hypixel_data)

        self.timezone, self.reset_hour = self._get_time_info()


    def _get_time_info(self):
        reset_time = rotational.get_dynamic_reset_time(self.uuid)

        timezone = f'GMT{statalib.prefix_int(reset_time.utc_offset)}:00'
        reset_hour = HOUR_LIST[reset_time.reset_hour]

        return timezone, reset_hour


class HistoricalRotationalStats(calctools.BedwarsStats):
    def __init__(
        self,
        uuid: str,
        period_id: rotational.HistoricalRotationPeriodID,
        hypixel_data: dict,
        mode: str='overall'
    ) -> None:
        super().__init__(hypixel_data, strict_mode=mode)

        self.historical_stats = rotational.RotationalStatsManager(uuid) \
            .get_historical_rotation_data(period_id.to_string())

        self.uuid = uuid
        self.mode = calctools.get_mode(mode)

        self.rank_info = calctools.get_rank_info(self._hypixel_data)

        level = self.historical_stats.level

        self.level = int(level)

        xp_total = calctools.xp_from_level(level)
        xp_gained = self.historical_stats.data.Experience
        stars_gained = level - calctools.get_level(xp_total - xp_gained)

        self.stars_gained = f"{calctools.rround(stars_gained, 2):,}"

        self.items_purchased_cum = self._get_stat('items_purchased_bedwars')

        self.games_played_cum = self._get_stat('games_played_bedwars')
        self.most_played_cum = self._get_most_played()
        self.timezone, self.reset_hour = self._get_time_info()

        self.wins_cum = self._get_stat('wins_bedwars')
        self.losses_cum = self._get_stat('losses_bedwars')
        self.wlr_cum = calctools.ratio(self.wins_cum, self.losses_cum)

        self.final_kills_cum = self._get_stat('final_kills_bedwars')
        self.final_deaths_cum = self._get_stat('final_deaths_bedwars')
        self.fkdr_cum = calctools.ratio(self.final_kills_cum, self.final_deaths_cum)

        self.beds_broken_cum = self._get_stat('beds_broken_bedwars')
        self.beds_lost_cum = self._get_stat('beds_lost_bedwars')
        self.bblr_cum = calctools.ratio(self.beds_broken_cum, self.beds_lost_cum)

        self.kills_cum = self._get_stat('kills_bedwars')
        self.deaths_cum = self._get_stat('deaths_bedwars')
        self.kdr_cum = calctools.ratio(self.kills_cum, self.deaths_cum)


    def _get_stat(self, key: str, default=0):
        return self.historical_stats.data.as_dict().get(f'{self.mode}{key}', default)


    def _get_most_played(self):
        return calctools.get_most_mode(
            self.historical_stats.data.as_dict(), 'games_played_bedwars')


    def _get_time_info(self):
        reset_time = rotational.get_dynamic_reset_time(self.uuid)

        timezone = f'GMT{statalib.prefix_int(reset_time.utc_offset)}:00'
        reset_hour = HOUR_LIST[reset_time.reset_hour]

        return timezone, reset_hour
