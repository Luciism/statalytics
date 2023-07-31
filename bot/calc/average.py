from statalib.calctools import (
    BedwarsStats,
    get_rank_info,
    rround,
)


class Ratios(BedwarsStats):
    def __init__(
        self,
        hypixel_data: dict,
        mode: str='overall'
    ) -> None:
        super().__init__(hypixel_data, strict_mode=mode.lower())

        self._level_real = self.experience / 5000
        self.level = int(self.level)

        self.rank_info = get_rank_info(self._hypixel_data)


    def get_per_star(self):
        per_star_vals = (
            self.wins, self.final_kills, self.beds_broken, self.kills,
            self.losses, self.final_deaths, self.beds_lost, self.deaths
        )
        results = []
        for val in per_star_vals:
            results.append(rround(val / (self._level_real or 1), 2))
        return results


    def get_per_game(self):
        per_game_vals = (
            self.final_kills, self.beds_broken, self.kills, self.deaths
        )
        
        results = []
        for val in per_game_vals:
            results.append(rround(val / (self.games_played or 1), 2))

        results.append(rround(self.games_played / (self.final_deaths or 1), 2))
        results.append(rround(self.games_played / (self.beds_lost or 1), 2))

        return results


    def get_clutch_rate(self):
        clutches = self.beds_lost - self.losses

        clutch_rate = rround((clutches / (self.beds_lost or -1)) * 100, 2)
        return f"{max(clutch_rate, 0)}%"


    def get_win_rate(self):
        win_rate = rround((self.wins / (self.games_played or -1)) * 100, 2)
        return f'{max(win_rate, 0)}%'


    def get_loss_rate(self):
        loss_rate = rround((self.losses / (self.games_played or -1)) * 100, 2)
        return f'{max(loss_rate, 0)}%'


    def get_most_wins(self):
        modes_dict = {
            'Solos': self._bedwars_data.get('eight_one_wins_bedwars', 0),
            'Doubles': self._bedwars_data.get('eight_two_wins_bedwars', 0),
            'Threes':  self._bedwars_data.get('four_three_wins_bedwars', 0),
            'Fours': self._bedwars_data.get('four_four_wins_bedwars', 0),
            '4v4': self._bedwars_data.get('two_four_wins_bedwars', 0)
        }
        if max(modes_dict.values()) == 0:
            return "N/A"
        return str(max(modes_dict, key=modes_dict.get))


    def get_most_losses(self):
        modes_dict = {
            'Solos': self._bedwars_data.get('eight_one_losses_bedwars', 0),
            'Doubles': self._bedwars_data.get('eight_two_losses_bedwars', 0),
            'Threes':  self._bedwars_data.get('four_three_losses_bedwars', 0),
            'Fours': self._bedwars_data.get('four_four_losses_bedwars', 0),
            '4v4': self._bedwars_data.get('two_four_losses_bedwars', 0)
        }
        if max(modes_dict.values()) == 0:
            return "N/A"
        return str(max(modes_dict, key=modes_dict.get))
