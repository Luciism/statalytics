class Resources:
    def __init__(self, name: str, mode: str, hypixel_data: dict) -> None:
        self.name = name
        self.mode = mode

        self.hypixel_data = hypixel_data.get('player', {}) if hypixel_data.get('player', {}) is not None else {}
        self.hypixel_data_bedwars = self.hypixel_data.get('stats', {}).get('Bedwars', {})

        self.mode = {"Solos": "eight_one_", "Doubles": "eight_two_", "Threes": "four_three_", "Fours": "four_four_"}.get(mode, "")

        self.level = self.hypixel_data.get("achievements", {}).get("bedwars_level", 0)
        self.games_played = self.hypixel_data_bedwars.get(f'{self.mode}games_played_bedwars', 0)
        self.total_resources = self.hypixel_data_bedwars.get(f'{self.mode}resources_collected_bedwars', 0)

        self.iron_collected = self.hypixel_data_bedwars.get(f'{self.mode}iron_resources_collected_bedwars', 0)
        self.gold_collected = self.hypixel_data_bedwars.get(f'{self.mode}gold_resources_collected_bedwars', 0)
        self.diamonds_collected = self.hypixel_data_bedwars.get(f'{self.mode}diamond_resources_collected_bedwars', 0)
        self.emeralds_collected = self.hypixel_data_bedwars.get(f'{self.mode}emerald_resources_collected_bedwars', 0)

    def get_player_rank_info(self):
        rank_info = {
            'rank': self.hypixel_data.get('rank', 'NONE') if self.name != "Technoblade" else "TECHNO",
            'packageRank': self.hypixel_data.get('packageRank', 'NONE'),
            'newPackageRank': self.hypixel_data.get('newPackageRank', 'NONE'),
            'monthlyPackageRank': self.hypixel_data.get('monthlyPackageRank', 'NONE'),
            'rankPlusColor': self.hypixel_data.get('rankPlusColor', None) if self.name != "Technoblade" else "AQUA"
        }
        return rank_info

    def get_progress(self):
        experience = self.hypixel_data_bedwars.get('Experience', 0)
        times_prestiged = int(self.level / 100)
        total_xp = 487000 * times_prestiged
        if (self.level < 100 and self.level > 4) or int(str(self.level)[-2:]) >= 4:
            total_xp += 7000
            xp_this_prestige = experience - total_xp
            xp_progress = xp_this_prestige % 5000
            target = 5000
        else:
            xp_this_prestige = experience - total_xp
            xp_map = {0: 500, 1: 1000, 2: 2000, 3: 3500, 4: 5000}
            xp_progress = xp_this_prestige
            target = 0
            for key in xp_map.keys():
                if int(str(self.level)[-2:]) == key:
                    if key != 0:
                        xp_before_this_level = sum([xp_map[i] for i in range(key)])
                        xp_progress = xp_this_prestige - xp_before_this_level
                    target = xp_map[key]
                    break
        devide_by = target / 10
        progress_out_of_ten = round(xp_progress / devide_by)
        return f'{xp_progress:,}', f'{target:,}', progress_out_of_ten

    def get_per_game(self):
        iron_per_game = round(0 if self.iron_collected == 0 else self.iron_collected / self.games_played if self.games_played != 0 else self.iron_collected, 2)
        gold_per_game = round(0 if self.gold_collected == 0 else self.gold_collected / self.games_played if self.games_played != 0 else self.gold_collected, 2)
        diamonds_per_game = round(0 if self.diamonds_collected == 0 else self.diamonds_collected / self.games_played if self.games_played != 0 else self.diamonds_collected, 2)
        emeralds_per_game = round(0 if self.emeralds_collected == 0 else self.emeralds_collected / self.games_played if self.games_played != 0 else self.emeralds_collected, 2)

        return f'{iron_per_game:,}', f'{gold_per_game:,}', f'{diamonds_per_game:,}', f'{emeralds_per_game:,}'

    def get_per_star(self):
        iron_per_star = round(0 if self.iron_collected == 0 else self.iron_collected / self.level if self.level != 0 else self.iron_collected, 2)
        gold_per_star = round(0 if self.gold_collected == 0 else self.gold_collected / self.level if self.level != 0 else self.gold_collected, 2)
        diamonds_per_star = round(0 if self.diamonds_collected == 0 else self.diamonds_collected / self.level if self.level != 0 else self.diamonds_collected, 2)
        emeralds_per_star = round(0 if self.emeralds_collected == 0 else self.emeralds_collected / self.level if self.level != 0 else self.emeralds_collected, 2)

        return f'{iron_per_star:,}', f'{gold_per_star:,}', f'{diamonds_per_star:,}', f'{emeralds_per_star:,}'

    def get_percentages(self):
        values = (self.iron_collected, self.gold_collected, self.diamonds_collected, self.emeralds_collected)
        return ('0%'if 0 in (value, self.total_resources) else f"{round((value / self.total_resources) * 100, 2)}%" for value in values)

    def get_most_modes(self):
        iron = {
            "Solos": self.hypixel_data_bedwars.get(f'eight_one_iron_resources_collected_bedwars', 0),
            "Doubles": self.hypixel_data_bedwars.get(f'eight_two_iron_resources_collected_bedwars', 0),
            "Threes": self.hypixel_data_bedwars.get(f'four_three_iron_resources_collected_bedwars', 0),
            "Fours": self.hypixel_data_bedwars.get(f'four_four_iron_resources_collected_bedwars', 0)
        }
        gold = {
            "Solos": self.hypixel_data_bedwars.get(f'eight_one_gold_resources_collected_bedwars', 0),
            "Doubles": self.hypixel_data_bedwars.get(f'eight_two_gold_resources_collected_bedwars', 0),
            "Threes": self.hypixel_data_bedwars.get(f'four_three_gold_resources_collected_bedwars', 0),
            "Fours": self.hypixel_data_bedwars.get(f'four_four_gold_resources_collected_bedwars', 0)
        }
        diamonds = {
            "Solos": self.hypixel_data_bedwars.get(f'eight_one_diamond_resources_collected_bedwars', 0),
            "Doubles": self.hypixel_data_bedwars.get(f'eight_two_diamond_resources_collected_bedwars', 0),
            "Threes": self.hypixel_data_bedwars.get(f'four_three_diamond_resources_collected_bedwars', 0),
            "Fours": self.hypixel_data_bedwars.get(f'four_four_diamond_resources_collected_bedwars', 0)
        }
        emeralds = {
            "Solos": self.hypixel_data_bedwars.get(f'eight_one_emerald_resources_collected_bedwars', 0),
            "Doubles": self.hypixel_data_bedwars.get(f'eight_two_emerald_resources_collected_bedwars', 0),
            "Threes": self.hypixel_data_bedwars.get(f'four_three_emerald_resources_collected_bedwars', 0),
            "Fours": self.hypixel_data_bedwars.get(f'four_four_emerald_resources_collected_bedwars', 0)
        }

        values = (iron, gold, diamonds, emeralds)
        return ("N/A" if max(value.values()) == 0 else str(max(value, key=value.get)) for value in values)
