from statalib.calctools import get_rank_info, get_level, get_player_dict


class ActiveCosmetics:
    def __init__(self, name: str, hypixel_data: dict) -> None:
        self.name = name

        self.hypixel_data = get_player_dict(hypixel_data)
        bedwars_data = self.hypixel_data.get('stats', {}).get('Bedwars', {})

        self.level = int(get_level(bedwars_data.get('Experience', 0)))

        def _get_cosmetic(key, replace):
            cosmetic = bedwars_data.get(key, 'none')
            return cosmetic.replace(replace, '').replace('_', ' ').title()

        self.shopkeeper_skin = _get_cosmetic('activeNPCSkin', 'npcskin_')
        self.projectile_trail = _get_cosmetic('activeProjectileTrail', 'projectiletrail_')
        self.death_cry = _get_cosmetic('activeDeathCry', 'deathcry_')
        self.wood_skin = _get_cosmetic('activeWoodType', 'woodSkin_')
        self.kill_effect = _get_cosmetic('activeKillEffect', 'killeffect_')
        self.island_topper = _get_cosmetic('activeIslandTopper', 'islandtopper_')
        self.victory_dance = _get_cosmetic('activeVictoryDance', 'victorydance_')
        self.glyph = _get_cosmetic('activeGlyph', 'glyph_')
        self.spray = _get_cosmetic('activeSprays', 'sprays_')
        self.bed_destroy = _get_cosmetic('activeBedDestroy', 'beddestroy_')
        self.kill_message = _get_cosmetic('activeKillMessages', 'killmessages_')

        self.rank_info = get_rank_info(self.hypixel_data)
