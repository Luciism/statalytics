class Ratios:
    def __init__(self, name, uuid, mode, hypixel_data) -> None:
        self.name, self.uuid = name, uuid
        self.mode = mode

        self.hypixel_data = hypixel_data.get('player', {}) if hypixel_data.get('player', {}) is not None else {}
        self.hypixel_data_bedwars = self.hypixel_data.get('stats', {}).get('Bedwars', {})

        self.mode = {"Solos": "eight_one_", "Doubles": "eight_two_", "Threes": "four_three_", "Fours": "four_four_"}.get(mode, "")

        self.level = self.hypixel_data.get("achievements", {}).get("bedwars_level", 0)
        self.games_played = self.hypixel_data_bedwars.get(f'{self.mode}games_played_bedwars', 0)

    def get_player_rank_info(self):
        rank_info = {
            'rank': self.hypixel_data.get('rank', 'NONE') if self.name != "Technoblade" else "TECHNO",
            'packageRank': self.hypixel_data.get('packageRank', 'NONE'),
            'newPackageRank': self.hypixel_data.get('newPackageRank', 'NONE'),
            'monthlyPackageRank': self.hypixel_data.get('monthlyPackageRank', 'NONE'),
            'rankPlusColor': self.hypixel_data.get('rankPlusColor', None) if self.name != "Technoblade" else "AQUA"
        }
        return rank_info

    def get_per_star(self):
        wins = self.hypixel_data_bedwars.get(f'{self.mode}wins_bedwars', 0)
        wins_per_star = round(0 if wins == 0 else wins / self.level if self.level != 0 else wins, 2)

        final_kills = self.hypixel_data_bedwars.get(f'{self.mode}final_kills_bedwars', 0)
        final_kills_per_star = round(0 if final_kills == 0 else final_kills / self.level if self.level != 0 else final_kills, 2)

        beds_broken = self.hypixel_data_bedwars.get(f'{self.mode}beds_broken_bedwars', 0)
        beds_broken_per_star = round(0 if beds_broken == 0 else beds_broken / self.level if self.level != 0 else beds_broken, 2)

        kills = self.hypixel_data_bedwars.get(f'{self.mode}kills_bedwars', 0)
        kills_per_star = round(0 if kills == 0 else kills / self.level if self.level != 0 else kills, 2)

        losses = self.hypixel_data_bedwars.get(f'{self.mode}losses_bedwars', 0)
        losses_per_star = round(0 if losses == 0 else losses / self.level if self.level != 0 else losses, 2)

        final_deaths = self.hypixel_data_bedwars.get(f'{self.mode}final_deaths_bedwars', 0)
        final_deaths_per_star = round(0 if final_deaths == 0 else final_deaths / self.level if self.level != 0 else final_deaths, 2)

        beds_lost = self.hypixel_data_bedwars.get(f'{self.mode}beds_lost_bedwars', 0)
        beds_lost_per_star = round(0 if beds_lost == 0 else beds_lost / self.level if self.level != 0 else beds_lost, 2)

        deaths = self.hypixel_data_bedwars.get(f'{self.mode}deaths_bedwars', 0)
        deaths_per_star = round(0 if deaths == 0 else deaths / self.level if self.level != 0 else deaths, 2)

        return str(wins_per_star), str(final_kills_per_star), str(beds_broken_per_star), str(kills_per_star), str(losses_per_star), str(final_deaths_per_star), str(beds_lost_per_star), str(deaths_per_star)

    def get_per_game(self):
        final_kills = self.hypixel_data_bedwars.get(f'{self.mode}final_kills_bedwars', 0)
        final_kills_per_game = round(0 if final_kills == 0 else final_kills / self.games_played if self.games_played != 0 else final_kills, 2)

        beds_broken = self.hypixel_data_bedwars.get(f'{self.mode}beds_broken_bedwars', 0)
        beds_broken_per_game = round(0 if beds_broken == 0 else beds_broken / self.games_played if self.games_played != 0 else beds_broken, 2)

        kills = self.hypixel_data_bedwars.get(f'{self.mode}kills_bedwars', 0)
        kills_per_game = round(0 if kills == 0 else kills / self.games_played if self.games_played != 0 else kills, 2)

        final_deaths = self.hypixel_data_bedwars.get(f'{self.mode}final_deaths_bedwars', 0)
        final_deaths_per_game = round(0 if final_deaths == 0 else final_deaths / self.games_played if self.games_played != 0 else final_deaths, 2)

        beds_lost = self.hypixel_data_bedwars.get(f'{self.mode}beds_lost_bedwars', 0)
        beds_lost_per_game = round(0 if beds_lost == 0 else beds_lost / self.games_played if self.games_played != 0 else beds_lost, 2)

        deaths = self.hypixel_data_bedwars.get(f'{self.mode}deaths_bedwars', 0)
        deaths_per_game = round(0 if deaths == 0 else deaths / self.games_played if self.games_played != 0 else deaths, 2)

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
