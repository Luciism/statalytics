from helper.calctools import get_player_rank_info


class ActiveCosmetics:
    def __init__(self, name: str, hypixel_data: dict) -> None:
        self.hypixel_data = hypixel_data.get('player', {})\
                            if hypixel_data.get('player', {}) is not None else {}
        bedwars_data = self.hypixel_data.get('stats', {}).get('Bedwars', {})
        self.name = name

        self.level = self.hypixel_data.get("achievements", {}).get("bedwars_level", 0)

        def get_cosmetic(key, replace):
            cosmetic = bedwars_data.get(key, 'none')
            return cosmetic.replace(replace, '').replace('_', ' ').title()

        self.shopkeeper_skin = get_cosmetic('activeNPCSkin', 'npcskin_')
        self.projectile_trail = get_cosmetic('activeProjectileTrail', 'projectiletrail_')
        self.death_cry = get_cosmetic('activeDeathCry', 'deathcry_')
        self.wood_skin = get_cosmetic('activeWoodType', 'woodSkin_')
        self.kill_effect = get_cosmetic('activeKillEffect', 'killeffect_')
        self.island_topper = get_cosmetic('activeIslandTopper', 'islandtopper_')
        self.victory_dance = get_cosmetic('activeVictoryDance', 'victorydance_')
        self.glyph = get_cosmetic('activeGlyph', 'glyph_')
        self.spray = get_cosmetic('activeSprays', 'sprays_')
        self.bed_destroy = get_cosmetic('activeBedDestroy', 'beddestroy_')
        self.kill_message = get_cosmetic('activeKillMessages', 'killmessages_')
        
        self.player_rank_info = get_player_rank_info(self.hypixel_data)
