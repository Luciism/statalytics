from helper.calctools import get_player_rank_info, get_mode, rround

class Ratios:
    def __init__(self, name: str, mode: str, hypixel_data: dict) -> None:
        self.name = name
        self.mode = get_mode(mode)

        self.hypixel_data = hypixel_data.get('player', {}) if hypixel_data.get('player', {}) is not None else {}
        self.hypixel_data_bedwars = self.hypixel_data.get('stats', {}).get('Bedwars', {})

        self.level = self.hypixel_data.get("achievements", {}).get("bedwars_level", 0)
        self.games_played = self.hypixel_data_bedwars.get(f'{self.mode}games_played_bedwars', 0)
        self.player_rank_info = get_player_rank_info(self.hypixel_data)

    def get_per_star(self):
        wins = self.hypixel_data_bedwars.get(f'{self.mode}wins_bedwars', 0)
        wins_per_star = rround(wins / (self.level or 1), 2)

        final_kills = self.hypixel_data_bedwars.get(f'{self.mode}final_kills_bedwars', 0)
        final_kills_per_star = rround(final_kills / (self.level or 1), 2)

        beds_broken = self.hypixel_data_bedwars.get(f'{self.mode}beds_broken_bedwars', 0)
        beds_broken_per_star = rround(beds_broken / (self.level or 1), 2)

        kills = self.hypixel_data_bedwars.get(f'{self.mode}kills_bedwars', 0)
        kills_per_star = rround(kills / (self.level or 1), 2)

        losses = self.hypixel_data_bedwars.get(f'{self.mode}losses_bedwars', 0)
        losses_per_star = rround(losses / (self.level or 1), 2)

        final_deaths = self.hypixel_data_bedwars.get(f'{self.mode}final_deaths_bedwars', 0)
        final_deaths_per_star = rround(final_deaths / (self.level or 1), 2)

        beds_lost = self.hypixel_data_bedwars.get(f'{self.mode}beds_lost_bedwars', 0)
        beds_lost_per_star = rround(beds_lost / (self.level or 1), 2)

        deaths = self.hypixel_data_bedwars.get(f'{self.mode}deaths_bedwars', 0)
        deaths_per_star = rround(deaths / (self.level or 1), 2)

        return str(wins_per_star), str(final_kills_per_star), str(beds_broken_per_star), str(kills_per_star), str(losses_per_star), str(final_deaths_per_star), str(beds_lost_per_star), str(deaths_per_star)

    def get_per_game(self):
        final_kills = self.hypixel_data_bedwars.get(f'{self.mode}final_kills_bedwars', 0)
        final_kills_per_game = rround(final_kills / (self.games_played or 1), 2)

        beds_broken = self.hypixel_data_bedwars.get(f'{self.mode}beds_broken_bedwars', 0)
        beds_broken_per_game = rround(beds_broken / (self.games_played or 1), 2)

        kills = self.hypixel_data_bedwars.get(f'{self.mode}kills_bedwars', 0)
        kills_per_game = rround(kills / (self.games_played or 1), 2)

        final_deaths = self.hypixel_data_bedwars.get(f'{self.mode}final_deaths_bedwars', 0)
        final_deaths_per_game = rround(final_deaths / (self.games_played or 1), 2)

        beds_lost = self.hypixel_data_bedwars.get(f'{self.mode}beds_lost_bedwars', 0)
        beds_lost_per_game = rround(beds_lost / (self.games_played or 1), 2)

        deaths = self.hypixel_data_bedwars.get(f'{self.mode}deaths_bedwars', 0)
        deaths_per_game = rround(deaths / (self.games_played or 1), 2)

        return str(final_kills_per_game), str(beds_broken_per_game), str(kills_per_game), str(final_deaths_per_game), str(beds_lost_per_game), str(deaths_per_game)

    def get_clutch_rate(self):
        losses = self.hypixel_data_bedwars.get(f'{self.mode}losses_bedwars', 0)
        beds_lost = self.hypixel_data_bedwars.get(f'{self.mode}beds_lost_bedwars', 0)
        clutches = beds_lost - losses
        return '0%' if clutches <= 0 or beds_lost <= 0 else f"{round((clutches / beds_lost) * 100, 2)}%"

    def get_loss_rate(self):
        losses = self.hypixel_data_bedwars.get(f'{self.mode}losses_bedwars', 0)
        return "0%" if self.games_played == 0 else "100%" if losses == 0 else f'{round((losses / self.games_played) * 100, 2)}%'

    def get_most_wins(self):
        solos = self.hypixel_data_bedwars.get('eight_one_wins_bedwars', 0)
        doubles = self.hypixel_data_bedwars.get('eight_two_wins_bedwars', 0)
        threes = self.hypixel_data_bedwars.get('four_three_wins_bedwars', 0)
        fours = self.hypixel_data_bedwars.get('four_four_wins_bedwars', 0)
        findgreatest = {'Solos': solos, 'Doubles': doubles, 'Threes':  threes, 'Fours': fours}
        return "Unknown" if max(findgreatest.values()) == 0 else str(max(findgreatest, key=findgreatest.get))

    def get_most_losses(self):
        solos = self.hypixel_data_bedwars.get('eight_one_losses_bedwars', 0)
        doubles = self.hypixel_data_bedwars.get('eight_two_losses_bedwars', 0)
        threes = self.hypixel_data_bedwars.get('four_three_losses_bedwars', 0)
        fours = self.hypixel_data_bedwars.get('four_four_losses_bedwars', 0)
        findgreatest = {'Solos': solos, 'Doubles': doubles, 'Threes':  threes, 'Fours': fours}
        return "Unknown" if max(findgreatest.values()) == 0 else str(max(findgreatest, key=findgreatest.get))
