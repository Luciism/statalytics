from statalib.hypixel import (
    BedwarsStats,
    rround,
    get_rank_info,
    real_title_case,
    BEDWARS_MODES_MAP
)


class ResourcesStats(BedwarsStats):
    def __init__(
        self,
        hypixel_data: dict,
        mode: str='overall'
    ) -> None:
        super().__init__(hypixel_data, ganemode=mode)

        self.rank_info = get_rank_info(self._hypixel_player_data)
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
        resources = {'iron': {}, 'gold': {}, 'diamond': {}, 'emerald': {}}
        for resource in resources:
            for mode, prefix in BEDWARS_MODES_MAP.items():
                if prefix:
                    resources[resource][real_title_case(mode)] = self._bedwars_data.get(
                        f'{prefix}{resource}_resources_collected_bedwars', 0)

        return_values = []
        for resource, values in resources.items():
            if max(values.values()) == 0:
                return_values.append('N/A')
            else:
                return_values.append(str(max(values, key=values.get, default='N/A')))

        return return_values
