from statalib.hypixel import (
    BedwarsStats,
    get_rank_info,
    rround,
    ratio,
    get_most_mode
)


class AverageStats(BedwarsStats):
    def __init__(
        self,
        hypixel_data: dict,
        mode: str='overall'
    ) -> None:
        super().__init__(hypixel_data, ganemode=mode.lower())

        self._level_real = self.questless_exp / 5000
        self.level = int(self.level)

        self.rank_info = get_rank_info(self._hypixel_data)

        self.wins_per_star = ratio(self.wins, self._level_real)
        self.final_kills_per_star = ratio(self.final_kills, self._level_real)
        self.beds_broken_per_star = ratio(self.beds_broken, self._level_real)
        self.kills_per_star = ratio(self.kills, self._level_real)

        self.losses_per_star = ratio(self.losses, self._level_real)
        self.final_deaths_per_star = ratio(self.final_deaths, self._level_real)
        self.beds_lost_per_star = ratio(self.beds_lost, self._level_real)
        self.deaths_per_star = ratio(self.deaths, self._level_real)

        self.final_kills_per_game = ratio(self.final_kills, self.games_played)
        self.beds_broken_per_game = ratio(self.beds_broken, self.games_played)
        self.kills_per_game = ratio(self.kills, self.games_played)
        self.deaths_per_game = ratio(self.deaths, self.games_played)

        self.games_per_final_death = ratio(self.games_played, self.final_deaths)
        self.games_per_bed_lost = ratio(self.games_played, self.beds_lost)

        self._clutch_rate = None
        self._win_rate = None
        self._loss_rate = None

        self._most_wins_mode = None
        self._most_losses_mode = None


    def _get_percent(self, dividend: int, divisor: int, round_by: int=2):
        rate = (dividend / (divisor or -1)) * 100
        return f'{max(rround(rate, round_by), 0)}%'


    @property
    def clutch_rate(self):
        """Percentage of games won without a bed"""
        if self._clutch_rate is None:
            clutches = self.beds_lost - self.losses
            self._clutch_rate = self._get_percent(clutches, self.beds_lost)
        return self._clutch_rate


    @property
    def win_rate(self):
        """Percentage of games won"""
        if self._win_rate is None:
            self._win_rate = self._get_percent(self.wins, self.games_played)
        return self._win_rate


    @property
    def loss_rate(self):
        """Percentate of games losses"""
        if self._loss_rate is None:
            self._loss_rate = self._get_percent(self.losses, self.games_played)
        return self._loss_rate


    @property
    def most_wins_mode(self):
        """Mode that the player has gained the most wins"""
        if self._most_wins_mode is None:
            self._most_wins_mode = get_most_mode(self._bedwars_data, 'wins_bedwars')
        return self._most_wins_mode


    @property
    def most_losses_mode(self):
        """Mode that the player has gained the most losses"""
        if self._most_losses_mode is None:
            self._most_losses_mode = get_most_mode(self._bedwars_data, 'losses_bedwars')
        return self._most_losses_mode
