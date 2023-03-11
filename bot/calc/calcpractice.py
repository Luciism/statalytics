import os
import random
import json
import requests

class Practice:
    def __init__(self, name, uuid) -> None:
        self.name, self.uuid = name, uuid

        with open(f'{os.getcwd()}/database/apikeys.json', 'r') as keyfile:
            allkeys = json.load(keyfile)['keys']
        key = random.choice(list(allkeys))

        response = requests.get(f"https://api.hypixel.net/player?key={allkeys[key]}&uuid={uuid}", timeout=10)
        self.hypixel_data = response.json().get('player', {}) if response.json().get('player', {}) is not None else {}
        self.practice_stats = self.hypixel_data.get('stats', {}).get('Bedwars', {}).get('practice', {})

        self.level = self.hypixel_data.get("achievements", {}).get("bedwars_level", 0)

    def get_player_rank_info(self):
        rank_info = {
            'rank': self.hypixel_data.get('rank', 'NONE') if self.name != "Technoblade" else "TECHNO",
            'packageRank': self.hypixel_data.get('packageRank', 'NONE'),
            'newPackageRank': self.hypixel_data.get('newPackageRank', 'NONE'),
            'monthlyPackageRank': self.hypixel_data.get('monthlyPackageRank', 'NONE'),
            'rankPlusColor': self.hypixel_data.get('rankPlusColor', None) if self.name != "Technoblade" else "AQUA"
        }
        return rank_info

    def get_bridging_stats(self):
        bridging_completed = self.practice_stats.get('bridging', {}).get('successful_attempts', 0)
        bridging_failed = self.practice_stats.get('bridging', {}).get('failed_attempts', 0)
        bridging_blocks = self.practice_stats.get('bridging', {}).get('blocks_placed', 0)
        bridging_ratio = round(0 if bridging_completed == 0 else bridging_completed / bridging_failed if bridging_failed != 0 else bridging_completed, 2)
        return f'{bridging_completed:,}', f'{bridging_failed:,}', f'{bridging_blocks:,}', f'{bridging_ratio:,}'

    def get_tnt_stats(self):
        tnt_completed = self.practice_stats.get('fireball_jumping', {}).get('successful_attempts', 0)
        tnt_failed = self.practice_stats.get('fireball_jumping', {}).get('failed_attempts', 0)
        tnt_blocks = self.practice_stats.get('fireball_jumping', {}).get('blocks_placed', 0)
        tnt_ratio = round(0 if tnt_completed == 0 else tnt_completed / tnt_failed if tnt_failed != 0 else tnt_completed, 2)
        return f'{tnt_completed:,}', f'{tnt_failed:,}', f'{tnt_blocks:,}', f'{tnt_ratio:,}'

    def get_mlg_stats(self):
        mlg_completed = self.practice_stats.get('mlg', {}).get('successful_attempts', 0)
        mlg_failed = self.practice_stats.get('mlg', {}).get('failed_attempts', 0)
        mlg_blocks = self.practice_stats.get('mlg', {}).get('blocks_placed', 0)
        mlg_ratio = round(0 if mlg_completed == 0 else mlg_completed / mlg_failed if mlg_failed != 0 else mlg_completed, 2)
        return f'{mlg_completed:,}', f'{mlg_failed:,}', f'{mlg_blocks:,}', f'{mlg_ratio:,}'

    def get_straight_times(self):
        short = round(self.practice_stats.get('records', {}).get('bridging_distance_30:elevation_NONE:angle_STRAIGHT:', 0) / 1000, 2)
        medium = round(self.practice_stats.get('records', {}).get('bridging_distance_50:elevation_NONE:angle_STRAIGHT:', 0) / 1000, 2)
        long = round(self.practice_stats.get('records', {}).get('bridging_distance_100:elevation_NONE:angle_STRAIGHT:', 0) / 1000, 2)
        average = round((short + medium + long) / 3, 2)
        return f'{short} seconds', f'{medium} seconds', f'{long} seconds', f'{average} seconds'

    def get_diagonal_times(self):
        short = round(self.practice_stats.get('records', {}).get('bridging_distance_30:elevation_NONE:angle_DIAGONAL:', 0) / 1000, 2)
        medium = round(self.practice_stats.get('records', {}).get('bridging_distance_50:elevation_NONE:angle_DIAGONAL:', 0) / 1000, 2)
        long = round(self.practice_stats.get('records', {}).get('bridging_distance_100:elevation_NONE:angle_DIAGONAL:', 0) / 1000, 2)
        average = round((short + medium + long) / 3, 2)
        return f'{short} seconds', f'{medium} seconds', f'{long} seconds', f'{average} seconds'

    def get_most_played(self):
        total_bridging = self.practice_stats.get('bridging', {}).get('successful_attempts', 0) + self.practice_stats.get('bridging', {}).get('failed_attempts', 0)
        total_tnt = self.practice_stats.get('fireball_jumping', {}).get('successful_attempts', 0) + self.practice_stats.get('fireball_jumping', {}).get('failed_attempts', 0)
        total_mlg = self.practice_stats.get('mlg', {}).get('successful_attempts', 0) + self.practice_stats.get('mlg', {}).get('failed_attempts', 0)
        findgreatest = {
            'BRIDGING': total_bridging,
            'TNT / FIREBALL': total_tnt,
            'MLG':  total_mlg
        }
        if max(findgreatest.values()) == 0:
            return "Undefined"
        return str(max(findgreatest, key=findgreatest.get))
