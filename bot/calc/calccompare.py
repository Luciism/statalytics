class Compare:
    def __init__(self, name_1: str, name_2: str, mode: str, hypixel_data_1: dict, hypixel_data_2) -> None:
        self.name_1, self.name_2 = name_1, name_2
        self.mode = mode

        self.hypixel_data_1 = hypixel_data_1.get('player', {}) if hypixel_data_1.get('player', {}) is not None else {}
        self.hypixel_data_2 = hypixel_data_2.get('player', {}) if hypixel_data_2.get('player', {}) is not None else {}
        self.hypixel_data_bedwars_1 = self.hypixel_data_1.get('stats', {}).get('Bedwars', {})
        self.hypixel_data_bedwars_2 = self.hypixel_data_2.get('stats', {}).get('Bedwars', {})

        self.mode = {"Solos": "eight_one_", "Doubles": "eight_two_", "Threes": "four_three_", "Fours": "four_four_"}.get(mode, "")

        self.level_1 = self.hypixel_data_1.get("achievements", {}).get("bedwars_level", 0)
        self.level_2 = self.hypixel_data_2.get("achievements", {}).get("bedwars_level", 0)

    def get_player_rank_info(self):
        rank_info_1 = {
            'rank': self.hypixel_data_1.get('rank', 'NONE') if self.name_1 != "Technoblade" else "TECHNO",
            'packageRank': self.hypixel_data_1.get('packageRank', 'NONE'),
            'newPackageRank': self.hypixel_data_1.get('newPackageRank', 'NONE'),
            'monthlyPackageRank': self.hypixel_data_1.get('monthlyPackageRank', 'NONE'),
            'rankPlusColor': self.hypixel_data_1.get('rankPlusColor', None) if self.name_1 != "Technoblade" else "AQUA"
        }
        rank_info_2 = {
            'rank': self.hypixel_data_2.get('rank', 'NONE') if self.name_2 != "Technoblade" else "TECHNO",
            'packageRank': self.hypixel_data_2.get('packageRank', 'NONE'),
            'newPackageRank': self.hypixel_data_2.get('newPackageRank', 'NONE'),
            'monthlyPackageRank': self.hypixel_data_2.get('monthlyPackageRank', 'NONE'),
            'rankPlusColor': self.hypixel_data_2.get('rankPlusColor', None) if self.name_2 != "Technoblade" else "AQUA"
        }
        return rank_info_1, rank_info_2
    
    def get_wins(self):
        wins_1 = self.hypixel_data_bedwars_1.get(f'{self.mode}wins_bedwars', 0)
        losses_1 = self.hypixel_data_bedwars_1.get(f'{self.mode}losses_bedwars', 0)
        wlr_1 = round(0 if wins_1 == 0 else wins_1 / losses_1 if losses_1 != 0 else wins_1, 2)

        wins_2 = self.hypixel_data_bedwars_2.get(f'{self.mode}wins_bedwars', 0)
        losses_2 = self.hypixel_data_bedwars_2.get(f'{self.mode}losses_bedwars', 0)
        wlr_2 = round(0 if wins_2 == 0 else wins_2 / losses_2 if losses_2 != 0 else wins_2, 2)

        wins_diff = wins_1 - wins_2
        wins_diff = f'{wins_diff:,}' if wins_diff < 0 else f'+{wins_diff:,}'

        losses_diff = losses_1 - losses_2
        losses_diff = f'{losses_diff:,}' if losses_diff < 0 else f'+{losses_diff:,}'

        wlr_diff = round(wlr_1 - wlr_2, 2)
        wlr_diff = f'{wlr_diff:,}' if wlr_diff < 0 else f'+{wlr_diff:,}'

        return f'{wins_1:,} / {wins_2:,}', f'{losses_1:,} / {losses_2:,}', f'{wlr_1:,} / {wlr_2:,}', wins_diff, losses_diff, wlr_diff

    def get_finals(self):
        final_kills_1 = self.hypixel_data_bedwars_1.get(f'{self.mode}final_kills_bedwars', 0)
        final_deaths_1 = self.hypixel_data_bedwars_1.get(f'{self.mode}final_deaths_bedwars', 0)
        fkdr_1 = round(0 if final_kills_1 == 0 else final_kills_1 / final_deaths_1 if final_deaths_1 != 0 else final_kills_1, 2)

        final_kills_2 = self.hypixel_data_bedwars_2.get(f'{self.mode}final_kills_bedwars', 0)
        final_deaths_2 = self.hypixel_data_bedwars_2.get(f'{self.mode}final_deaths_bedwars', 0)
        fkdr_2 = round(0 if final_kills_2 == 0 else final_kills_2 / final_deaths_2 if final_deaths_2 != 0 else final_kills_2, 2)

        final_kills_diff = final_kills_1 - final_kills_2
        final_kills_diff = f'{final_kills_diff:,}' if final_kills_diff < 0 else f'+{final_kills_diff:,}'

        final_deaths_diff = final_deaths_1 - final_deaths_2
        final_deaths_diff = f'{final_deaths_diff:,}' if final_deaths_diff < 0 else f'+{final_deaths_diff:,}'

        fkdr_diff = round(fkdr_1 - fkdr_2, 2)
        fkdr_diff = f'{fkdr_diff:,}' if fkdr_diff < 0 else f'+{fkdr_diff:,}'

        return f'{final_kills_1:,} / {final_kills_2:,}', f'{final_deaths_1:,} / {final_deaths_2:,}', f'{fkdr_1:,} / {fkdr_2:,}', final_kills_diff, final_deaths_diff, fkdr_diff

    def get_beds(self):
        beds_broken_1 = self.hypixel_data_bedwars_1.get(f'{self.mode}beds_broken_bedwars', 0)
        beds_lost_1 = self.hypixel_data_bedwars_1.get(f'{self.mode}beds_lost_bedwars', 0)
        bblr_1 = round(0 if beds_broken_1 == 0 else beds_broken_1 / beds_lost_1 if beds_lost_1 != 0 else beds_broken_1, 2)

        beds_broken_2 = self.hypixel_data_bedwars_2.get(f'{self.mode}beds_broken_bedwars', 0)
        beds_lost_2 = self.hypixel_data_bedwars_2.get(f'{self.mode}beds_lost_bedwars', 0)
        bblr_2 = round(0 if beds_broken_2 == 0 else beds_broken_2 / beds_lost_2 if beds_lost_2 != 0 else beds_broken_2, 2)

        beds_broken_diff = beds_broken_1 - beds_broken_2
        beds_broken_diff = f'{beds_broken_diff:,}' if beds_broken_diff < 0 else f'+{beds_broken_diff:,}'

        beds_lost_diff = beds_lost_1 - beds_lost_2
        beds_lost_diff = f'{beds_lost_diff:,}' if beds_lost_diff < 0 else f'+{beds_lost_diff:,}'

        bblr_diff = round(bblr_1 - bblr_2, 2)
        bblr_diff = f'{bblr_diff:,}' if bblr_diff < 0 else f'+{bblr_diff:,}'

        return f'{beds_broken_1:,} / {beds_broken_2:,}', f'{beds_lost_1:,} / {beds_lost_2:,}', f'{bblr_1:,} / {bblr_2:,}', beds_broken_diff, beds_lost_diff, bblr_diff

    def get_kills(self):
        kills_1 = self.hypixel_data_bedwars_1.get(f'{self.mode}kills_bedwars', 0)
        deaths_1 = self.hypixel_data_bedwars_1.get(f'{self.mode}deaths_bedwars', 0)
        kdr_1 = round(0 if deaths_1 == 0 else kills_1 / deaths_1 if deaths_1 != 0 else kills_1, 2)

        kills_2 = self.hypixel_data_bedwars_2.get(f'{self.mode}kills_bedwars', 0)
        deaths_2 = self.hypixel_data_bedwars_2.get(f'{self.mode}deaths_bedwars', 0)
        kdr_2 = round(0 if deaths_2 == 0 else kills_2 / deaths_2 if deaths_2 != 0 else kills_2, 2)

        kills_diff = kills_1 - kills_2
        kills_diff = f'{kills_diff:,}' if kills_diff < 0 else f'+{kills_diff:,}'

        deaths_diff = deaths_1 - deaths_2
        deaths_diff = f'{deaths_diff:,}' if deaths_diff < 0 else f'+{deaths_diff:,}'

        kdr_diff = round(kdr_1 - kdr_2, 2)
        kdr_diff = f'{kdr_diff:,}' if kdr_diff < 0 else f'+{kdr_diff:,}'

        return f'{kills_1:,} / {kills_2:,}', f'{deaths_1:,} / {deaths_2:,}', f'{kdr_1:,} / {kdr_2:,}', kills_diff, deaths_diff, kdr_diff
