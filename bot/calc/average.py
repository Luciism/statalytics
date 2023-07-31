from statalib.calctools import (
    get_rank_info,
    get_mode,
    rround,
    get_progress,
    get_level,
    get_player_dict
)


class Ratios:
    def __init__(self, name: str, mode: str, hypixel_data: dict) -> None:
        self.name = name
        self.mode = get_mode(mode)

        self.hypixel_data = get_player_dict(hypixel_data)
        self.hypixel_data_bedwars = self.hypixel_data.get('stats', {}).get('Bedwars', {})

        self.experience = self.hypixel_data_bedwars.get('Experience', 0)

        self.level_real = self.experience / 5000
        self.level = int(get_level(self.experience))

        self.games_played = self.hypixel_data_bedwars.get(f'{self.mode}games_played_bedwars', 0)

        self.rank_info = get_rank_info(self.hypixel_data)

        self.progress = get_progress(hypixel_data_bedwars=self.hypixel_data_bedwars)


    def get_per_star(self):
        wins = self.hypixel_data_bedwars.get(f'{self.mode}wins_bedwars', 0)
        wins_per_star = rround(wins / (self.level_real or 1), 2)

        final_kills = self.hypixel_data_bedwars.get(f'{self.mode}final_kills_bedwars', 0)
        final_kills_per_star = rround(final_kills / (self.level_real or 1), 2)

        beds_broken = self.hypixel_data_bedwars.get(f'{self.mode}beds_broken_bedwars', 0)
        beds_broken_per_star = rround(beds_broken / (self.level_real or 1), 2)

        kills = self.hypixel_data_bedwars.get(f'{self.mode}kills_bedwars', 0)
        kills_per_star = rround(kills / (self.level_real or 1), 2)

        losses = self.hypixel_data_bedwars.get(f'{self.mode}losses_bedwars', 0)
        losses_per_star = rround(losses / (self.level_real or 1), 2)

        final_deaths = self.hypixel_data_bedwars.get(f'{self.mode}final_deaths_bedwars', 0)
        final_deaths_per_star = rround(final_deaths / (self.level_real or 1), 2)

        beds_lost = self.hypixel_data_bedwars.get(f'{self.mode}beds_lost_bedwars', 0)
        beds_lost_per_star = rround(beds_lost / (self.level_real or 1), 2)

        deaths = self.hypixel_data_bedwars.get(f'{self.mode}deaths_bedwars', 0)
        deaths_per_star = rround(deaths / (self.level_real or 1), 2)

        return str(wins_per_star), str(final_kills_per_star), str(beds_broken_per_star),\
               str(kills_per_star), str(losses_per_star), str(final_deaths_per_star),\
               str(beds_lost_per_star), str(deaths_per_star)


    def get_per_game(self):
        final_kills = self.hypixel_data_bedwars.get(f'{self.mode}final_kills_bedwars', 0)
        final_kills_per_game = rround(final_kills / (self.games_played or 1), 2)

        beds_broken = self.hypixel_data_bedwars.get(f'{self.mode}beds_broken_bedwars', 0)
        beds_broken_per_game = rround(beds_broken / (self.games_played or 1), 2)

        kills = self.hypixel_data_bedwars.get(f'{self.mode}kills_bedwars', 0)
        kills_per_game = rround(kills / (self.games_played or 1), 2)

        final_deaths = self.hypixel_data_bedwars.get(f'{self.mode}final_deaths_bedwars', 0)
        games_per_final_death = rround(self.games_played / (final_deaths or 1), 2)

        beds_lost = self.hypixel_data_bedwars.get(f'{self.mode}beds_lost_bedwars', 0)
        games_per_bed_lost = rround(self.games_played / (beds_lost or 1), 2)

        deaths = self.hypixel_data_bedwars.get(f'{self.mode}deaths_bedwars', 0)
        deaths_per_game = rround(deaths / (self.games_played or 1), 2)

        return str(final_kills_per_game), str(beds_broken_per_game), str(kills_per_game),\
               str(games_per_final_death), str(games_per_bed_lost), str(deaths_per_game)


    def get_clutch_rate(self):
        losses = self.hypixel_data_bedwars.get(f'{self.mode}losses_bedwars', 0)
        beds_lost = self.hypixel_data_bedwars.get(f'{self.mode}beds_lost_bedwars', 0)
        clutches = beds_lost - losses

        clutch_rate = round((clutches / (beds_lost or -1)) * 100, 2)
        return f"{max(clutch_rate, 0)}%"


    def get_win_rate(self):
        wins = self.hypixel_data_bedwars.get(f'{self.mode}wins_bedwars', 0)

        win_rate = round((wins / (self.games_played or -1)) * 100, 2)
        return f'{max(win_rate, 0)}%'


    def get_loss_rate(self):
        losses = self.hypixel_data_bedwars.get(f'{self.mode}losses_bedwars', 0)

        loss_rate = round((losses / (self.games_played or -1)) * 100, 2)
        return f'{max(loss_rate, 0)}%'


    def get_most_wins(self):
        solos = self.hypixel_data_bedwars.get('eight_one_wins_bedwars', 0)
        doubles = self.hypixel_data_bedwars.get('eight_two_wins_bedwars', 0)
        threes = self.hypixel_data_bedwars.get('four_three_wins_bedwars', 0)
        fours = self.hypixel_data_bedwars.get('four_four_wins_bedwars', 0)
        four_vs_four: int = self.hypixel_data_bedwars.get('two_four_wins_bedwars', 0)
        modes_dict = {'Solos': solos, 'Doubles': doubles, 'Threes':  threes, 'Fours': fours, '4v4': four_vs_four}
        return "N/A" if max(modes_dict.values()) == 0 else str(max(modes_dict, key=modes_dict.get))


    def get_most_losses(self):
        solos = self.hypixel_data_bedwars.get('eight_one_losses_bedwars', 0)
        doubles = self.hypixel_data_bedwars.get('eight_two_losses_bedwars', 0)
        threes = self.hypixel_data_bedwars.get('four_three_losses_bedwars', 0)
        fours = self.hypixel_data_bedwars.get('four_four_losses_bedwars', 0)
        four_vs_four: int = self.hypixel_data_bedwars.get('two_four_losses_bedwars', 0)
        modes_dict = {'Solos': solos, 'Doubles': doubles, 'Threes':  threes, 'Fours': fours, '4v4': four_vs_four}
        return "N/A" if max(modes_dict.values()) == 0 else str(max(modes_dict, key=modes_dict.get))
