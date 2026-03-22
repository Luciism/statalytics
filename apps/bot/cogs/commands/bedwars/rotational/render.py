from datetime import datetime, timezone, timedelta
from typing import final
from statalib.hypixel import Leveling
from typing_extensions import override

import statalib as lib
from statalib import render2, rotational_stats
from statalib.rotational_stats import HistoricalRotationPeriodID, RotationType

from calc.rotational import HistoricalRotationalStats, RotationalStats

def format_rotation_date(rotation: RotationType, date: datetime) -> str:
    match rotation:
        case RotationType.DAILY | RotationType.WEEKLY:
            return date.strftime(f"%b {date.day}{lib.fmt.ordinal(date.day)}, %Y")
        case RotationType.MONTHLY:
            return date.strftime(f"%B %Y")
        case _:
            return date.strftime(f"%Y")

@final
class RotationalStatsRenderer(render2.RenderingClient):
    def __init__(
        self,
        skin_model_bytes: bytes,
        username: str,
        player_uuid: str,
        data: lib.HypixelData,
        period: RotationType | HistoricalRotationPeriodID,
        mode: lib.Mode,
        periods_ago: int=0
    ) -> None:
        super().__init__(route="rotational")

        self._skin_model_bytes = skin_model_bytes
        self._username = username
        self._player_uuid = player_uuid
        self._data = data
        self._period = period
        self._periods_ago = periods_ago
        self.mode = mode


    @override
    def placeholder_values(self) -> render2.PlaceholderValues:
        mode = self.mode or lib.ModesEnum.OVERALL.value
        if isinstance(self._period, RotationType):
            stats = RotationalStats(self._player_uuid, self._period, self._data, mode)
            rotation_type = self._period

            time_period = rotation_type.value.title()

            utc_offset = rotational_stats.get_dynamic_reset_time(self._player_uuid).utc_offset
            now = datetime.now(timezone(timedelta(hours=utc_offset)))
            rotation_value = format_rotation_date(rotation_type, now)

            experience = stats.experience_local
        else:
            stats = HistoricalRotationalStats(self._player_uuid, self._period, self._data, mode)
            rotation_type = self._period.rotation_type
            experience = stats.experience
            time_period = f"{self._periods_ago} {rotation_type.singular_name().title()}s Ago"

            rotation_value = format_rotation_date(rotation_type, self._period.datetime_info)


        leveling = Leveling(xp=experience)
        xp_progress = leveling.progression

        prestige = lib.render.Prestige(int(stats.level))
        prestige_gradient = prestige.colors.seven_step_gradient

        text_placeholders = {
            "stat_wins#text": f"{stats.wins_cum:,}",
            "stat_losses#text": f"{stats.losses_cum:,}",
            "stat_wlr#text": f"{stats.wlr_cum:,}",

            "stat_final_kills#text": f"{stats.final_kills_cum:,}",
            "stat_final_deaths#text": f"{stats.final_deaths_cum:,}",
            "stat_fkdr#text": f"{stats.fkdr_cum:,}",

            "stat_kills#text": f"{stats.kills_cum:,}",
            "stat_deaths#text": f"{stats.deaths_cum:,}",
            "stat_kdr#text": f"{stats.kdr_cum:,}",

            "stat_beds_broken#text": f"{stats.beds_broken_cum:,}",
            "stat_beds_lost#text": f"{stats.beds_lost_cum:,}",
            "stat_bblr#text": f"{stats.bblr_cum:,}",

            "stat_stars_gained#text": stats.stars_gained,
            "stat_games_played#text": f"{stats.games_played_cum:,}",
            "stat_most_played#text": stats.most_played_cum,

            "gamemode#text": mode.name,
            "time_period#text": time_period,

            "rotation_key#text": rotation_type.singular_name().title(),
            "rotation_value#text": rotation_value,
            "title#text": f"{rotation_type.value.title()} Stats",
        }


        placeholder_values = render2.PlaceholderValues.new(text=text_placeholders)
        placeholder_values.add_skin_model(self._skin_model_bytes)
        placeholder_values.add_footer_text()
        placeholder_values.add_progress_bar(prestige_gradient, xp_progress.progress_percent)
        placeholder_values.add_xp_progress_text(leveling.progression)
        placeholder_values.add_current_and_next_level(int(leveling.level_int))
        placeholder_values.add_playername(stats.get_rank_info(self._username))

        return placeholder_values

