import math

class Stats:
    def __init__(self, name, uuid, mode, hypixel_data) -> None:
        self.name, self.uuid = name, uuid
        self.mode = mode

        self.hypixel_data = hypixel_data.get('player', {}) if hypixel_data.get('player', {}) != None else {}
        self.hypixel_data_bedwars = self.hypixel_data.get('stats', {}).get('Bedwars', {})

        self.level = self.hypixel_data.get("achievements", {}).get("bedwars_level", 0)

        self.mode = {"Solos": "eight_one_", "Doubles": "eight_two_", "Threes": "four_three_", "Fours": "four_four_"}.get(mode, "")

    def get_player_rank(self):
        rank_info = {
            'rank': self.hypixel_data.get('rank', 'NONE'),
            'packageRank': self.hypixel_data.get('packageRank', 'NONE'),
            'newPackageRank': self.hypixel_data.get('newPackageRank', 'NONE'),
            'monthlyPackageRank': self.hypixel_data.get('monthlyPackageRank', 'NONE'),
            'rankPlusColor': self.hypixel_data.get('rankPlusColor', None)
        }
        return rank_info

    def get_wins_until_value(self):
        wins = self.hypixel_data_bedwars.get(f'{self.mode}wins_bedwars', 0)
        losses = self.hypixel_data_bedwars.get(f'{self.mode}losses_bedwars', 0)
        target_wlr = math.ceil(0 if wins == 0 else wins / losses if losses != 0 else wins)

        wins_at_target = int(losses * target_wlr)
        needed_wins = wins_at_target - wins
        return str("{:,}".format(needed_wins))

    def get_wins_at_value(self):
        wins = self.hypixel_data_bedwars.get(f'{self.mode}wins_bedwars', 0)
        losses = self.hypixel_data_bedwars.get(f'{self.mode}losses_bedwars', 0)
        target_wlr = math.ceil(0 if wins == 0 else wins / losses if losses != 0 else wins)

        wins_at_target = int(losses * target_wlr)
        return str("{:,}".format(wins_at_target))

    def get_wlr_target(self):
        wins = self.hypixel_data_bedwars.get(f'{self.mode}wins_bedwars', 0)
        losses = self.hypixel_data_bedwars.get(f'{self.mode}losses_bedwars', 0)
        target_wlr = math.ceil(0 if wins == 0 else wins / losses if losses != 0 else wins)
        return f'{str("{:,}".format(target_wlr))} WLR'

    def get_wins_until_wins_value(self):
        wins = self.hypixel_data_bedwars.get(f'{self.mode}wins_bedwars', 0)

        target_wins = (wins // 1000 + 1) * 1000
        needed_wins = target_wins - wins
        return str("{:,}".format(needed_wins))

    def get_wins_until_wins_target(self):
        wins = self.hypixel_data_bedwars.get(f'{self.mode}wins_bedwars', 0)

        target_wins = (wins // 1000 + 1) * 1000
        return str("{:,}".format(target_wins))

    def get_losses_until_losses_value(self):
        losses = self.hypixel_data_bedwars.get(f'{self.mode}losses_bedwars', 0)

        target_losses = (losses // 1000 + 1) * 1000
        needed_losses = target_losses - losses
        return str("{:,}".format(needed_losses))

    def get_losses_until_losses_target(self):
        losses = self.hypixel_data_bedwars.get(f'{self.mode}losses_bedwars', 0)

        target_losses = (losses // 1000 + 1) * 1000
        return str("{:,}".format(target_losses))

    # --

    def get_final_kills_until_value(self):
        final_kills = self.hypixel_data_bedwars.get(f'{self.mode}final_kills_bedwars', 0)
        final_deaths = self.hypixel_data_bedwars.get(f'{self.mode}final_deaths_bedwars', 0)
        target_fkdr = math.ceil(0 if final_kills == 0 else final_kills / final_deaths if final_deaths != 0 else final_kills)

        final_kills_at_target = int(final_deaths * target_fkdr)
        needed_final_kills = final_kills_at_target - final_kills
        return str("{:,}".format(needed_final_kills))

    def get_final_kills_at_value(self):
        final_kills = self.hypixel_data_bedwars.get(f'{self.mode}final_kills_bedwars', 0)
        final_deaths = self.hypixel_data_bedwars.get(f'{self.mode}final_deaths_bedwars', 0)
        target_fkdr = math.ceil(0 if final_kills == 0 else final_kills / final_deaths if final_deaths != 0 else final_kills)

        final_kills_at_target = int(final_deaths * target_fkdr)
        return str("{:,}".format(final_kills_at_target))

    def get_fkdr_target(self):
        final_kills = self.hypixel_data_bedwars.get(f'{self.mode}final_kills_bedwars', 0)
        final_deaths = self.hypixel_data_bedwars.get(f'{self.mode}final_deaths_bedwars', 0)
        target_fkdr = math.ceil(0 if final_kills == 0 else final_kills / final_deaths if final_deaths != 0 else final_kills)
        return f'{str("{:,}".format(target_fkdr))} FKDR'

    def get_final_kills_until_final_kills_value(self):
        final_kills = self.hypixel_data_bedwars.get(f'{self.mode}final_kills_bedwars', 0)

        target_final_kills = (final_kills // 1000 + 1) * 1000
        needed_final_kills = target_final_kills - final_kills
        return str("{:,}".format(needed_final_kills))

    def get_final_kills_until_final_kills_target(self):
        final_kills = self.hypixel_data_bedwars.get(f'{self.mode}final_kills_bedwars', 0)

        target_final_kills = (final_kills // 1000 + 1) * 1000
        return str("{:,}".format(target_final_kills))

    def get_final_deaths_until_final_deaths_value(self):
        final_deaths = self.hypixel_data_bedwars.get(f'{self.mode}final_deaths_bedwars', 0)

        target_final_deaths = (final_deaths // 1000 + 1) * 1000
        needed_final_deaths = target_final_deaths - final_deaths
        return str("{:,}".format(needed_final_deaths))

    def get_final_deaths_until_final_deaths_target(self):
        final_deaths = self.hypixel_data_bedwars.get(f'{self.mode}final_deaths_bedwars', 0)

        target_final_deaths = (final_deaths // 1000 + 1) * 1000
        return str("{:,}".format(target_final_deaths))

    # --

    def get_beds_broken_until_value(self):
        beds_broken = self.hypixel_data_bedwars.get(f'{self.mode}beds_broken_bedwars', 0)
        beds_lost = self.hypixel_data_bedwars.get(f'{self.mode}beds_lost_bedwars', 0)
        target_bblr = math.ceil(0 if beds_broken == 0 else beds_broken / beds_lost if beds_lost != 0 else beds_broken)

        beds_broken_at_target = int(beds_lost * target_bblr)
        needed_beds_broken = beds_broken_at_target - beds_broken
        return str("{:,}".format(needed_beds_broken))

    def get_beds_broken_at_value(self):
        beds_broken = self.hypixel_data_bedwars.get(f'{self.mode}beds_broken_bedwars', 0)
        beds_lost = self.hypixel_data_bedwars.get(f'{self.mode}beds_lost_bedwars', 0)
        target_bblr = math.ceil(0 if beds_broken == 0 else beds_broken / beds_lost if beds_lost != 0 else beds_broken)

        beds_broken_at_target = int(beds_lost * target_bblr)
        return str("{:,}".format(beds_broken_at_target))

    def get_bblr_target(self):
        beds_broken = self.hypixel_data_bedwars.get(f'{self.mode}beds_broken_bedwars', 0)
        beds_lost = self.hypixel_data_bedwars.get(f'{self.mode}beds_lost_bedwars', 0)
        target_bblr = math.ceil(0 if beds_broken == 0 else beds_broken / beds_lost if beds_lost != 0 else beds_broken)
        return f'{str("{:,}".format(target_bblr))} BBLR'

    def get_beds_broken_until_beds_broken_value(self):
        beds_broken = self.hypixel_data_bedwars.get(f'{self.mode}beds_broken_bedwars', 0)

        target_beds_broken = (beds_broken // 1000 + 1) * 1000
        needed_beds_broken = target_beds_broken - beds_broken
        return str("{:,}".format(needed_beds_broken))

    def get_beds_broken_until_beds_broken_target(self):
        beds_broken = self.hypixel_data_bedwars.get(f'{self.mode}beds_broken_bedwars', 0)

        target_beds_broken = (beds_broken // 1000 + 1) * 1000
        return str("{:,}".format(target_beds_broken))

    def get_beds_lost_until_beds_lost_value(self):
        beds_lost = self.hypixel_data_bedwars.get(f'{self.mode}beds_lost_bedwars', 0)

        target_beds_lost = (beds_lost // 1000 + 1) * 1000
        needed_beds_lost = target_beds_lost - beds_lost
        return str("{:,}".format(needed_beds_lost))

    def get_beds_lost_until_beds_lost_target(self):
        beds_lost = self.hypixel_data_bedwars.get(f'{self.mode}beds_lost_bedwars', 0)

        target_beds_lost = (beds_lost // 1000 + 1) * 1000
        return str("{:,}".format(target_beds_lost))

    # --

    def get_kills_until_value(self):
        kills = self.hypixel_data_bedwars.get(f'{self.mode}kills_bedwars', 0)
        deaths = self.hypixel_data_bedwars.get(f'{self.mode}deaths_bedwars', 0)
        target_kdr = math.ceil(0 if kills == 0 else kills / deaths if deaths != 0 else kills)

        kills_at_target = int(deaths * target_kdr)
        needed_kills = kills_at_target - kills
        return str("{:,}".format(needed_kills))

    def get_kills_at_value(self):
        kills = self.hypixel_data_bedwars.get(f'{self.mode}kills_bedwars', 0)
        deaths = self.hypixel_data_bedwars.get(f'{self.mode}deaths_bedwars', 0)
        target_kdr = math.ceil(0 if kills == 0 else kills / deaths if deaths != 0 else kills)

        kills_at_target = int(deaths * target_kdr)
        return str("{:,}".format(kills_at_target))

    def get_kdr_target(self):
        kills = self.hypixel_data_bedwars.get(f'{self.mode}kills_bedwars', 0)
        deaths = self.hypixel_data_bedwars.get(f'{self.mode}deaths_bedwars', 0)
        target_kdr = math.ceil(0 if kills == 0 else kills / deaths if deaths != 0 else kills)
        return f'{str("{:,}".format(target_kdr))} KDR'

    def get_kills_until_kills_value(self):
        kills = self.hypixel_data_bedwars.get(f'{self.mode}kills_bedwars', 0)

        target_kills = (kills // 1000 + 1) * 1000
        needed_kills = target_kills - kills
        return str("{:,}".format(needed_kills))

    def get_kills_until_kills_target(self):
        kills = self.hypixel_data_bedwars.get(f'{self.mode}kills_bedwars', 0)

        target_kills = (kills // 1000 + 1) * 1000
        return str("{:,}".format(target_kills))

    def get_deaths_until_deaths_value(self):
        deaths = self.hypixel_data_bedwars.get(f'{self.mode}deaths_bedwars', 0)

        target_deaths = (deaths // 1000 + 1) * 1000
        needed_deaths = target_deaths - deaths
        return str("{:,}".format(needed_deaths))

    def get_deaths_until_deaths_target(self):
        deaths = self.hypixel_data_bedwars.get(f'{self.mode}deaths_bedwars', 0)

        target_deaths = (deaths // 1000 + 1) * 1000
        return str("{:,}".format(target_deaths))

    # --

    def get_stars_value(self):
        level_target = (self.level // 100 + 1) * 100
        needed_levels = level_target - self.level
        return str(needed_levels)

    def get_stars_target(self):
        level_target = (self.level // 100 + 1) * 100
        return str(level_target)
