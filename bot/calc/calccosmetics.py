import json
import os
import random
import requests

class ActiveCosmetics:
    def __init__(self, name, uuid) -> None:
        self.name, self.uuid = name, uuid

        with open(f'{os.getcwd()}/database/apikeys.json', 'r') as keyfile:
            allkeys = json.load(keyfile)['keys']
        key = random.choice(list(allkeys))

        response = requests.get(f"https://api.hypixel.net/player?key={allkeys[key]}&uuid={uuid}", timeout=10)
        self.hypixel_data = response.json().get('player', {}) if response.json().get('player', {}) is not None else {}

        self.level = self.hypixel_data.get("achievements", {}).get("bedwars_level", 0)

        self.shopkeeper_skin = self.hypixel_data.get('stats', {}).get('Bedwars', {}).get('activeNPCSkin', 'npcskin_none').replace('npcskin_', '').replace('_', ' ').title()
        self.projectile_trail = self.hypixel_data.get('stats', {}).get('Bedwars', {}).get('activeProjectileTrail', 'projectiletrail_none').replace('projectiletrail_', '').replace('_', ' ').title()
        self.death_cry = self.hypixel_data.get('stats', {}).get('Bedwars', {}).get('activeDeathCry', 'deathcry_none').replace('deathcry_', '').replace('_', ' ').title()
        self.wood_skin = self.hypixel_data.get('stats', {}).get('Bedwars', {}).get('activeWoodType', 'woodSkin_none').replace('woodSkin_', '').replace('_', ' ').title()
        self.kill_effect = self.hypixel_data.get('stats', {}).get('Bedwars', {}).get('activeKillEffect', 'killeffect_none').replace('killeffect_', '').replace('_', ' ').title()
        self.island_topper = self.hypixel_data.get('stats', {}).get('Bedwars', {}).get('activeIslandTopper', 'islandtopper_none').replace('islandtopper_', '').replace('_', ' ').title()
        self.victory_dance = self.hypixel_data.get('stats', {}).get('Bedwars', {}).get('activeVictoryDance', 'victorydance_none').replace('victorydance_', '').replace('_', ' ').title()
        self.glyph = self.hypixel_data.get('stats', {}).get('Bedwars', {}).get('activeGlyph', 'glyph_none').lower().replace('glyph_', '').replace('_', ' ').title()
        self.spray = self.hypixel_data.get('stats', {}).get('Bedwars', {}).get('activeSprays', 'sprays_none').replace('sprays_', '').replace('_', ' ').title()
        self.bed_destroy = self.hypixel_data.get('stats', {}).get('Bedwars', {}).get('activeBedDestroy', 'beddestroy_none').replace('beddestroy_', '').replace('_', ' ').title()
        self.kill_message = self.hypixel_data.get('stats', {}).get('Bedwars', {}).get('activeKillMessages', 'killmessages_none').replace('killmessages_', '').replace('_', ' ').title()

    def get_player_rank(self):
        rank_info = {
            'rank': self.hypixel_data.get('rank', 'NONE'),
            'packageRank': self.hypixel_data.get('packageRank', 'NONE'),
            'newPackageRank': self.hypixel_data.get('newPackageRank', 'NONE'),
            'monthlyPackageRank': self.hypixel_data.get('monthlyPackageRank', 'NONE'),
            'rankPlusColor': self.hypixel_data.get('rankPlusColor', None)
        }
        return rank_info
