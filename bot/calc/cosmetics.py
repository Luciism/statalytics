from helper.calctools import get_player_rank_info

class ActiveCosmetics:
    def __init__(self, hypixel_data: dict) -> None:
        self.hypixel_data = hypixel_data.get('player', {}) if hypixel_data.get('player', {}) is not None else {}
        bedwars_data = self.hypixel_data.get('stats', {}).get('Bedwars', {})
        self.name = hypixel_data.get('displayname', None)

        self.level = self.hypixel_data.get("achievements", {}).get("bedwars_level", 0)

        self.shopkeeper_skin = bedwars_data.get('activeNPCSkin', 'npcskin_none').replace('npcskin_', '').replace('_', ' ').title()
        self.projectile_trail = bedwars_data.get('activeProjectileTrail', 'projectiletrail_none').replace('projectiletrail_', '').replace('_', ' ').title()
        self.death_cry = bedwars_data.get('activeDeathCry', 'deathcry_none').replace('deathcry_', '').replace('_', ' ').title()
        self.wood_skin = bedwars_data.get('activeWoodType', 'woodSkin_none').replace('woodSkin_', '').replace('_', ' ').title()
        self.kill_effect = bedwars_data.get('activeKillEffect', 'killeffect_none').replace('killeffect_', '').replace('_', ' ').title()
        self.island_topper = bedwars_data.get('activeIslandTopper', 'islandtopper_none').replace('islandtopper_', '').replace('_', ' ').title()
        self.victory_dance = bedwars_data.get('activeVictoryDance', 'victorydance_none').replace('victorydance_', '').replace('_', ' ').title()
        self.glyph = bedwars_data.get('activeGlyph', 'glyph_none').lower().replace('glyph_', '').replace('_', ' ').title()
        self.spray = bedwars_data.get('activeSprays', 'sprays_none').replace('sprays_', '').replace('_', ' ').title()
        self.bed_destroy = bedwars_data.get('activeBedDestroy', 'beddestroy_none').replace('beddestroy_', '').replace('_', ' ').title()
        self.kill_message = bedwars_data.get('activeKillMessages', 'killmessages_none').replace('killmessages_', '').replace('_', ' ').title()

        self.player_rank_info = get_player_rank_info(self.hypixel_data)

