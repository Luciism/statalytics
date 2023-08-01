from statalib.calctools import (
    BedwarsStats,
    rround,
    get_rank_info,
)


class ResourcesStats(BedwarsStats):
    def __init__(
        self,
        hypixel_data: dict,
        mode: str='overall'
    ) -> None:
        super().__init__(hypixel_data, strict_mode=mode)

        self.rank_info = get_rank_info(self._hypixel_data)
        self.level = int(self.level)


    def get_per_game(self):
        iron_per_game = rround(self.iron_collected / (self.games_played or 1), 2)
        gold_per_game = rround(self.gold_collected / (self.games_played or 1), 2)
        diamonds_per_game = rround(self.diamonds_collected / (self.games_played or 1), 2)
        emeralds_per_game = rround(self.emeralds_collected / (self.games_played or 1), 2)

        return f'{iron_per_game:,}', f'{gold_per_game:,}',\
               f'{diamonds_per_game:,}', f'{emeralds_per_game:,}'


    def get_per_star(self):
        iron_per_star = rround(self.iron_collected / (self.level or 1), 2)
        gold_per_star = rround(self.gold_collected / (self.level or 1), 2)
        diamonds_per_star = rround(self.diamonds_collected / (self.level or 1), 2)
        emeralds_per_star = rround(self.emeralds_collected / (self.level or 1), 2)

        return f'{iron_per_star:,}', f'{gold_per_star:,}',\
               f'{diamonds_per_star:,}', f'{emeralds_per_star:,}'


    def get_percentages(self):
        values = (self.iron_collected, self.gold_collected,
                  self.diamonds_collected, self.emeralds_collected)
        
        return_values = []
        for value in values:
            if 0 in (value, self.resources_collected):
                return_values.append('0%')
            else:
                return_values.append(
                    f"{round((value / self.resources_collected) * 100, 2)}%")

        return return_values


    def get_most_modes(self):
        iron = {
            "Solos": self._bedwars_data.get('eight_one_iron_resources_collected_bedwars', 0),
            "Doubles": self._bedwars_data.get('eight_two_iron_resources_collected_bedwars', 0),
            "Threes": self._bedwars_data.get('four_three_iron_resources_collected_bedwars', 0),
            "Fours": self._bedwars_data.get('four_four_iron_resources_collected_bedwars', 0)
        }
        gold = {
            "Solos": self._bedwars_data.get('eight_one_gold_resources_collected_bedwars', 0),
            "Doubles": self._bedwars_data.get('eight_two_gold_resources_collected_bedwars', 0),
            "Threes": self._bedwars_data.get('four_three_gold_resources_collected_bedwars', 0),
            "Fours": self._bedwars_data.get('four_four_gold_resources_collected_bedwars', 0)
        }
        diamonds = {
            "Solos": self._bedwars_data.get('eight_one_diamond_resources_collected_bedwars', 0),
            "Doubles": self._bedwars_data.get('eight_two_diamond_resources_collected_bedwars', 0),
            "Threes": self._bedwars_data.get('four_three_diamond_resources_collected_bedwars', 0),
            "Fours": self._bedwars_data.get('four_four_diamond_resources_collected_bedwars', 0)
        }
        emeralds = {
            "Solos": self._bedwars_data.get('eight_one_emerald_resources_collected_bedwars', 0),
            "Doubles": self._bedwars_data.get('eight_two_emerald_resources_collected_bedwars', 0),
            "Threes": self._bedwars_data.get('four_three_emerald_resources_collected_bedwars', 0),
            "Fours": self._bedwars_data.get('four_four_emerald_resources_collected_bedwars', 0)
        }

        values = (iron, gold, diamonds, emeralds)
        return ("N/A" if max(value.values()) == 0 else\
                str(max(value, key=value.get)) for value in values)
