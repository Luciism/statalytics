from statalib.functions import format_seconds
from statalib.hypixel import (
    BedwarsStats,
    get_rank_info,
    Leveling,
    rround
)

"""
quest_map = {
    "bedwars_daily_win": "First Win of the Day",
    "bedwars_daily_one_more": "One More Game!",
    "bedwars_daily_bed_breaker": "Painsomnia",
    "bedwars_daily_final_killer": "Head Hunter",
    "bedwars_weekly_bed_elims": "Bed Removal Co.",
    "bedwars_weekly_dream_win": "Sleep Tight.",
    "bedwars_weekly_challenges": "Challenger",
    "bedwars_weekly_challenges_win": "Challenger",
    "bedwars_weekly_final_killer": "Finishing the Job"
}
"""

class QuestStats(BedwarsStats):
    def __init__(
        self,
        hypixel_data: dict,
    ) -> None:
        super().__init__(hypixel_data, ganemode='overall')

        self.rank_info = get_rank_info(self._hypixel_data)

        self.questless_level = Leveling(xp=self.questless_exp).level
        self.questless_star = int(self.questless_level)

        self.stars_from_quests = int(self.level - self.questless_level)

        self.stars = int(self.level)

        self.quests_completed = self.quests_data.get('completions', 0)

        self.lvls_daily_win, self.completions_daily_win = (
            self._calc_quest('bedwars_daily_win'))

        self.lvls_daily_one_more, self.completions_daily_one_more = (
            self._calc_quest('bedwars_daily_one_more'))

        self.lvls_daily_bed_breaker, self.completions_daily_bed_breaker = (
            self._calc_quest('bedwars_daily_bed_breaker'))

        self.lvls_daily_final_killer, self.completions_daily_final_killer = (
            self._calc_quest('bedwars_daily_final_killer'))

        self.lvls_weekly_bed_elims, self.completions_weekly_bed_elims = (
            self._calc_quest('bedwars_weekly_bed_elims'))

        self.lvls_weekly_dream_win, self.completions_weekly_dream_win = (
            self._calc_quest('bedwars_weekly_dream_win'))

        self.lvls_weekly_challenges_win, self.completions_weekly_challenges_win = (
            self._calc_quest('bedwars_weekly_challenges_win'))

        self.lvls_weekly_final_killer, self.completions_weekly_final_killer = (
            self._calc_quest('bedwars_weekly_final_killer'))

        self._estimated_playtime = None
        self._formatted_estimated_playtime = None

        self._wins_per_hour = None
        self._final_kills_per_hour = None

        self._hours_per_star = None
        self._questless_hours_per_star = None

        self._real_exp = None

    @property
    def real_exp(self):
        """Player's exp without win exp or quest exp"""
        if self._real_exp is None:
            self._real_exp = self.questless_exp - self.wins_xp
        return self._real_exp

    @property
    def estimated_playtime(self):
        """Estimated playtime in seconds"""
        if self._estimated_playtime is None:
            self._estimated_playtime = int(self.real_exp / 25 * 60)
        return self._estimated_playtime

    @property
    def formatted_estimated_playtime(self):
        """Estimated playtime formatted dynamically as a string"""
        if self._formatted_estimated_playtime is None:
            self._formatted_estimated_playtime = format_seconds(self.estimated_playtime)
        return self._formatted_estimated_playtime

    @property
    def hours_per_star(self):
        if self._hours_per_star is None:
            hours_playtime = self.real_exp / 25 / 60
            hours_per_star = hours_playtime / (self.level or 1)
            self._hours_per_star = rround(hours_per_star, 2)
        return self._hours_per_star

    @property
    def questless_hours_per_star(self):
        if self._questless_hours_per_star is None:
            hours_playtime = self.real_exp / 25 / 60
            hours_per_star = hours_playtime / (self.questless_level or 1)
            self._questless_hours_per_star = rround(hours_per_star, 2)
        return self._questless_hours_per_star

    @property
    def wins_per_hour(self):
        if self._wins_per_hour is None:
            self._wins_per_hour = self._per_hour(self.wins)
        return self._wins_per_hour

    @property
    def final_kills_per_hour(self):
        if self._final_kills_per_hour is None:
            self._final_kills_per_hour = self._per_hour(self.final_kills)
        return self._final_kills_per_hour


    def _per_hour(self, value: int):
        hours_playtime = self.real_exp / 25 / 60
        per_hour = value / (hours_playtime or 1)
        return rround(per_hour, 2)


    def _calc_quest(self, quest: str) -> tuple[int, int]:
        quest_data = self.quests_data['quests_exp'].get(quest, {})
        quest_levels = quest_data.get('experience', 0) // 5000
        completions = quest_data.get('completions', 0)

        if quest == 'bedwars_weekly_challenges_win':
            quest_data: dict = self.quests_data['quests_exp'].get(
                'bedwars_weekly_challenges', {})

            quest_levels += quest_data.get('experience', 0) // 5000
            completions += quest_data.get('completions', 0)

        return quest_levels, completions
