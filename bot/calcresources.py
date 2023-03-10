class Resources:
    def __init__(self, name, uuid, mode, hypixel_data) -> None:
        self.name, self.uuid = name, uuid
        self.mode = mode

        self.hypixel_data = hypixel_data.get('player', {}) if hypixel_data.get('player', {}) is not None else {}
        self.hypixel_data_bedwars = self.hypixel_data.get('stats', {}).get('Bedwars', {})

        self.mode = {"Solos": "eight_one_", "Doubles": "eight_two_", "Threes": "four_three_", "Fours": "four_four_"}.get(mode, "")

        self.level = self.hypixel_data.get("achievements", {}).get("bedwars_level", 0)
        self.games_played = self.hypixel_data_bedwars.get(f'{self.mode}games_played_bedwars', 0)
        self.total_resources = self.hypixel_data_bedwars.get(f'{self.mode}resources_collected_bedwars', 0)

    def get_player_rank(self):
        rank_info = {
            'rank': self.hypixel_data.get('rank', 'NONE'),
            'packageRank': self.hypixel_data.get('packageRank', 'NONE'),
            'newPackageRank': self.hypixel_data.get('newPackageRank', 'NONE'),
            'monthlyPackageRank': self.hypixel_data.get('monthlyPackageRank', 'NONE'),
            'rankPlusColor': self.hypixel_data.get('rankPlusColor', None)
        }
        return rank_info

    def get_collected(self):
        iron_collected = self.hypixel_data_bedwars.get(f'{self.mode}iron_resources_collected_bedwars', 0)
        gold_collected = self.hypixel_data_bedwars.get(f'{self.mode}gold_resources_collected_bedwars', 0)
        diamonds_collected = self.hypixel_data_bedwars.get(f'{self.mode}diamond_resources_collected_bedwars', 0)
        emeralds_collected = self.hypixel_data_bedwars.get(f'{self.mode}emerald_resources_collected_bedwars', 0)
        return f'{iron_collected:,}', f'{gold_collected:,}', f'{diamonds_collected:,}', f'{emeralds_collected:,}'

    def get_per_game(self):
        iron_collected = self.hypixel_data_bedwars.get(f'{self.mode}iron_resources_collected_bedwars', 0)
        iron_per_game = round(0 if iron_collected == 0 else iron_collected / self.games_played if self.games_played != 0 else iron_collected, 2)

        gold_collected = self.hypixel_data_bedwars.get(f'{self.mode}gold_resources_collected_bedwars', 0)
        gold_per_game = round(0 if gold_collected == 0 else gold_collected / self.games_played if self.games_played != 0 else gold_collected, 2)

        diamonds_collected = self.hypixel_data_bedwars.get(f'{self.mode}diamond_resources_collected_bedwars', 0)
        diamonds_per_game = round(0 if diamonds_collected == 0 else diamonds_collected / self.games_played if self.games_played != 0 else diamonds_collected, 2)

        emeralds_collected = self.hypixel_data_bedwars.get(f'{self.mode}emerald_resources_collected_bedwars', 0)
        emeralds_per_game = round(0 if emeralds_collected == 0 else emeralds_collected / self.games_played if self.games_played != 0 else emeralds_collected, 2)

        return f'{iron_per_game:,}', f'{gold_per_game:,}', f'{diamonds_per_game:,}', f'{emeralds_per_game:,}'

    def get_per_star(self):
        iron_collected = self.hypixel_data_bedwars.get(f'{self.mode}iron_resources_collected_bedwars', 0)
        iron_per_star = round(0 if iron_collected == 0 else iron_collected / self.level if self.level != 0 else iron_collected, 2)

        gold_collected = self.hypixel_data_bedwars.get(f'{self.mode}gold_resources_collected_bedwars', 0)
        gold_per_star = round(0 if gold_collected == 0 else gold_collected / self.level if self.level != 0 else gold_collected, 2)

        diamonds_collected = self.hypixel_data_bedwars.get(f'{self.mode}diamond_resources_collected_bedwars', 0)
        diamonds_per_star = round(0 if diamonds_collected == 0 else diamonds_collected / self.level if self.level != 0 else diamonds_collected, 2)

        emeralds_collected = self.hypixel_data_bedwars.get(f'{self.mode}emerald_resources_collected_bedwars', 0)
        emeralds_per_star = round(0 if emeralds_collected == 0 else emeralds_collected / self.level if self.level != 0 else emeralds_collected, 2)

        return f'{iron_per_star:,}', f'{gold_per_star:,}', f'{diamonds_per_star:,}', f'{emeralds_per_star:,}'

    def get_iron_percentage(self):
        iron_collected = self.hypixel_data_bedwars.get(f'{self.mode}iron_resources_collected_bedwars', 0)
        return '0%' if iron_collected == 0 or self.total_resources == 0 else f"{round((iron_collected / self.total_resources) * 100, 2)}%"

    def get_gold_percentage(self):
        gold_collected = self.hypixel_data_bedwars.get(f'{self.mode}gold_resources_collected_bedwars', 0)
        return '0%' if gold_collected == 0 or self.total_resources == 0 else f"{round((gold_collected / self.total_resources) * 100, 2)}%"

    def get_diamond_percentage(self):
        diamonds_collected = self.hypixel_data_bedwars.get(f'{self.mode}diamond_resources_collected_bedwars', 0)
        return '0%' if diamonds_collected == 0 or self.total_resources == 0 else f"{round((diamonds_collected / self.total_resources) * 100, 2)}%"

    def get_emerald_percentage(self):
        emeralds_collected = self.hypixel_data_bedwars.get(f'{self.mode}emerald_resources_collected_bedwars', 0)
        return '0%'if emeralds_collected == 0 or self.total_resources == 0 else f"{round((emeralds_collected / self.total_resources) * 100, 2)}%"
