import statalib
from statalib import hypixel, rotational_stats as rotational


def _get_reset_time_info(uuid: str) -> tuple[str, str]:
    reset_time = rotational.get_dynamic_reset_time(uuid)

    timezone = f'GMT{statalib.prefix_int(reset_time.utc_offset)}:00'

    reset_time = statalib.format_12hr_time(
        reset_time.reset_hour, reset_time.reset_minute)

    return timezone, reset_time


class RotationalStats(hypixel.CumulativeStats):
    def __init__(
        self,
        uuid: str,
        rotation_type: rotational.RotationType,
        hypixel_data: dict,
        mode: str='overall'
    ) -> None:
        self.rotational_data = rotational.RotationalStatsManager(uuid) \
            .get_rotational_data(rotation_type)

        super().__init__(hypixel_data, self.rotational_data.data, gamemode=mode)

        self.uuid = uuid
        self.mode = hypixel.mode_name_to_id(mode)

        self.stars_gained = f'{hypixel.rround(self.levels_cum, 2):,}'
        self.level = int(self.level)

        self.rank_info = hypixel.get_rank_info(self._hypixel_data)

        self.timezone, self.reset_time = _get_reset_time_info(self.uuid)



class HistoricalRotationalStats(hypixel.BedwarsStats):
    def __init__(
        self,
        uuid: str,
        period_id: rotational.HistoricalRotationPeriodID,
        hypixel_data: dict,
        mode: str='overall'
    ) -> None:
        super().__init__(hypixel_data, ganemode=mode)

        self.historical_stats = rotational.RotationalStatsManager(uuid) \
            .get_historical_rotation_data(period_id.to_string())

        self.uuid = uuid
        self.mode = hypixel.mode_name_to_id(mode)

        self.rank_info = hypixel.get_rank_info(self._hypixel_data)

        level = self.historical_stats.level

        self.level = int(level)

        xp_total = hypixel.Leveling(level=level).xp
        xp_gained = self.historical_stats.data.Experience
        stars_gained = level - hypixel.Leveling(xp=xp_total - xp_gained).level

        self.stars_gained = f"{hypixel.rround(stars_gained, 2):,}"

        self.items_purchased_cum = self._get_stat('items_purchased_bedwars')

        self.games_played_cum = self._get_stat('games_played_bedwars')
        self.most_played_cum = self._get_most_played()
        self.timezone, self.reset_time = _get_reset_time_info(self.uuid)

        self.wins_cum = self._get_stat('wins_bedwars')
        self.losses_cum = self._get_stat('losses_bedwars')
        self.wlr_cum = hypixel.ratio(self.wins_cum, self.losses_cum)

        self.final_kills_cum = self._get_stat('final_kills_bedwars')
        self.final_deaths_cum = self._get_stat('final_deaths_bedwars')
        self.fkdr_cum = hypixel.ratio(self.final_kills_cum, self.final_deaths_cum)

        self.beds_broken_cum = self._get_stat('beds_broken_bedwars')
        self.beds_lost_cum = self._get_stat('beds_lost_bedwars')
        self.bblr_cum = hypixel.ratio(self.beds_broken_cum, self.beds_lost_cum)

        self.kills_cum = self._get_stat('kills_bedwars')
        self.deaths_cum = self._get_stat('deaths_bedwars')
        self.kdr_cum = hypixel.ratio(self.kills_cum, self.deaths_cum)


    def _get_stat(self, key: str, default=0):
        return self.historical_stats.data.as_dict().get(f'{self.mode}{key}', default)


    def _get_most_played(self):
        return hypixel.get_most_mode(
            self.historical_stats.data.as_dict(), 'games_played_bedwars')
