from datetime import UTC, datetime, timedelta


from ..sessions import BedwarsSession
from .cumulative_stats import CumulativeStats
from .utils import ratio, rround


class ProjectedStats(CumulativeStats):
    def __init__(
        self,
        hypixel_data: dict,
        session_info: BedwarsSession,
        target_level: float=None,
        target_date: datetime=None,
        strict_mode: str='overall'
    ):
        """
        #### Either `target_level` or `target_date` must be provided but only one
        :param hypixel_data: the raw hypixel response json
        :param session_info: locally stored snapshot of a player's stats
        :param target_level: the level to predict stats for
        :param target_date: the date to predict the stats for
        :param strict_mode: the mode to fetch stats for (overall, solos, doubles, etc)
        """
        # Ensure either target_level or target_date was provided
        assert (target_level, target_date).count(None) == 1

        super().__init__(hypixel_data, session_info.data, strict_mode)

        now = datetime.now(UTC)

        session_start_time = datetime.fromtimestamp(
            session_info.creation_timestamp, UTC)
        self.session_duration_days = (now - session_start_time).days

        self.levels_per_day = ratio(self.levels_cum, self.session_duration_days)

        if target_level is None:
            self.days_to_go = (target_date - now).days or 1

            target_level = self.level + (self.levels_per_day * self.days_to_go)
            self.levels_to_go = target_level - self.level
        else:
            self.levels_to_go = target_level - self.level
            days_per_level_gained = (self.session_duration_days / (self.levels_cum or 1))

            self.days_to_go = int(days_per_level_gained * self.levels_to_go)

            try:
                target_date = now + timedelta(days=self.days_to_go)
            except OverflowError:
                target_date = None

        self.target_level = target_level
        self.target_date = target_date

        self.complete_percent = f"{round((self.level / (target_level or 1)) * 100, 2)}%"


        self.wins_projected = self._calc_projection(
            self.wins, self.wins_cum, increase=True)

        self.losses_projected = self._calc_projection(
            self.losses, self.losses_cum)

        self.wlr_projected = ratio(
            self.wins_projected, self.losses_projected)


        self.final_kills_projected = self._calc_projection(
            self.final_kills, self.final_kills_cum, increase=True)

        self.final_deaths_projected = self._calc_projection(
            self.final_deaths, self.final_deaths_cum)

        self.fkdr_projected = ratio(
            self.final_kills_projected, self.final_deaths_projected)


        self.beds_broken_projected = self._calc_projection(
            self.beds_broken, self.beds_broken_cum, increase=True)

        self.beds_lost_projected = self._calc_projection(
            self.beds_lost, self.beds_lost_cum)

        self.bblr_projected = ratio(
            self.beds_broken_projected, self.beds_lost_projected)


        self.kills_projected = self._calc_projection(
            self.kills, self.kills_cum, increase=True)

        self.deaths_projected = self._calc_projection(
            self.deaths, self.deaths_cum)

        self.kdr_projected = ratio(
            self.kills_projected, self.deaths_projected)


        self.items_purchased_projected = self._calc_projection(
                self.items_purchased, self.items_purchased_cum)

        self.wins_per_star = self._per_star(self.wins_projected, self.wins)
        self.kills_per_star = self._per_star(self.kills_projected, self.kills)

        self.final_kills_per_star = self._per_star(
            self.final_kills_projected, self.final_kills)

        self.beds_broken_per_star = self._per_star(
            self.beds_broken_projected, self.beds_broken)

        self._projection_date: str = None


    @property
    def projection_date(self):
        """Projected date formatted as `%b %d, %Y`"""
        if self._projection_date is None:
            if self.target_date is None:
                self._projection_date =  "Deceased"
            else:
                self._projection_date = self.target_date.strftime("%b %d, %Y")
        return self._projection_date


    def _per_star(self, projected_value: int, current_value: int):
        per_star = (projected_value - current_value) / (self.levels_to_go or 1)
        return rround(per_star, 2)


    def _calc_projection(self, current_value: int, cum_value: int, increase=True):
        value_per_day = cum_value / (self.session_duration_days or 1)
        added_value = value_per_day * self.days_to_go

        projected_value = current_value + added_value

        # Account for 0.02% skill increase per star gained
        if increase:
            projected_value += projected_value * 0.0002 * self.levels_to_go

        return int(projected_value)
