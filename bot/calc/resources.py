from helper.calctools import (get_mode, rround, get_progress,
                              get_player_rank_info, get_level, get_player_dict)


class Resources:
    def __init__(self, name: str, mode: str, hypixel_data: dict) -> None:
        self.name = name
        self.mode = get_mode(mode)

        self.hypixel_data = get_player_dict(hypixel_data)
        self.hypixel_data_bedwars = self.hypixel_data.get('stats', {}).get('Bedwars', {})

        self.progress = get_progress(self.hypixel_data_bedwars)
        self.player_rank_info = get_player_rank_info(self.hypixel_data)

        self.level = int(get_level(self.hypixel_data_bedwars.get('Experience', 0)))
        self.games_played = self.hypixel_data_bedwars.get(f'{self.mode}games_played_bedwars', 0)
        self.total_resources = self.hypixel_data_bedwars.get(f'{self.mode}resources_collected_bedwars', 0)

        self.iron_collected = self.hypixel_data_bedwars.get(f'{self.mode}iron_resources_collected_bedwars', 0)
        self.gold_collected = self.hypixel_data_bedwars.get(f'{self.mode}gold_resources_collected_bedwars', 0)
        self.diamonds_collected = self.hypixel_data_bedwars.get(f'{self.mode}diamond_resources_collected_bedwars', 0)
        self.emeralds_collected = self.hypixel_data_bedwars.get(f'{self.mode}emerald_resources_collected_bedwars', 0)


    def get_per_game(self):
        iron_per_game = rround(self.iron_collected / (self.games_played or 1), 2)
        gold_per_game = rround(self.gold_collected / (self.games_played or 1), 2)
        diamonds_per_game = rround(self.diamonds_collected / (self.games_played or 1), 2)
        emeralds_per_game = rround(self.emeralds_collected / (self.games_played or 1), 2)

        return f'{iron_per_game:,}', f'{gold_per_game:,}', f'{diamonds_per_game:,}', f'{emeralds_per_game:,}'


    def get_per_star(self):
        iron_per_star = rround(self.iron_collected / (self.level or 1), 2)
        gold_per_star = rround(self.gold_collected / (self.level or 1), 2)
        diamonds_per_star = rround(self.diamonds_collected / (self.level or 1), 2)
        emeralds_per_star = rround(self.emeralds_collected / (self.level or 1), 2)

        return f'{iron_per_star:,}', f'{gold_per_star:,}', f'{diamonds_per_star:,}', f'{emeralds_per_star:,}'


    def get_percentages(self):
        values = (self.iron_collected, self.gold_collected, self.diamonds_collected, self.emeralds_collected)
        return ('0%'if 0 in (value, self.total_resources)\
                else f"{round((value / self.total_resources) * 100, 2)}%" for value in values)


    def get_most_modes(self):
        iron = {
            "Solos": self.hypixel_data_bedwars.get('eight_one_iron_resources_collected_bedwars', 0),
            "Doubles": self.hypixel_data_bedwars.get('eight_two_iron_resources_collected_bedwars', 0),
            "Threes": self.hypixel_data_bedwars.get('four_three_iron_resources_collected_bedwars', 0),
            "Fours": self.hypixel_data_bedwars.get('four_four_iron_resources_collected_bedwars', 0)
        }
        gold = {
            "Solos": self.hypixel_data_bedwars.get('eight_one_gold_resources_collected_bedwars', 0),
            "Doubles": self.hypixel_data_bedwars.get('eight_two_gold_resources_collected_bedwars', 0),
            "Threes": self.hypixel_data_bedwars.get('four_three_gold_resources_collected_bedwars', 0),
            "Fours": self.hypixel_data_bedwars.get('four_four_gold_resources_collected_bedwars', 0)
        }
        diamonds = {
            "Solos": self.hypixel_data_bedwars.get('eight_one_diamond_resources_collected_bedwars', 0),
            "Doubles": self.hypixel_data_bedwars.get('eight_two_diamond_resources_collected_bedwars', 0),
            "Threes": self.hypixel_data_bedwars.get('four_three_diamond_resources_collected_bedwars', 0),
            "Fours": self.hypixel_data_bedwars.get('four_four_diamond_resources_collected_bedwars', 0)
        }
        emeralds = {
            "Solos": self.hypixel_data_bedwars.get('eight_one_emerald_resources_collected_bedwars', 0),
            "Doubles": self.hypixel_data_bedwars.get('eight_two_emerald_resources_collected_bedwars', 0),
            "Threes": self.hypixel_data_bedwars.get('four_three_emerald_resources_collected_bedwars', 0),
            "Fours": self.hypixel_data_bedwars.get('four_four_emerald_resources_collected_bedwars', 0)
        }

        values = (iron, gold, diamonds, emeralds)
        return ("N/A" if max(value.values()) == 0 else str(max(value, key=value.get)) for value in values)
