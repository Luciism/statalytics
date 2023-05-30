from helper.calctools import get_player_rank_info, get_progress, rround


class Practice:
    def __init__(self, name: str, hypixel_data: dict) -> None:
        self.name = name

        self.hypixel_data = hypixel_data.get('player', {}) if hypixel_data.get('player', {}) is not None else {}
        self.practice_stats = self.hypixel_data.get('stats', {}).get('Bedwars', {}).get('practice', {})

        self.level = self.hypixel_data.get("achievements", {}).get("bedwars_level", 0)
        self.player_rank_info = get_player_rank_info(self.hypixel_data)
        self.progress = get_progress(self.hypixel_data.get('stats', {}).get('Bedwars', {}))


    def get_bridging_stats(self):
        bridging_completed = self.practice_stats.get('bridging', {}).get('successful_attempts', 0)
        bridging_failed = self.practice_stats.get('bridging', {}).get('failed_attempts', 0)
        bridging_ratio = rround(bridging_completed / (bridging_failed or 1), 2)
        return f'{bridging_completed:,}', f'{bridging_failed:,}', f'{bridging_ratio:,}'


    def get_tnt_stats(self):
        tnt_completed = self.practice_stats.get('fireball_jumping', {}).get('successful_attempts', 0)
        tnt_failed = self.practice_stats.get('fireball_jumping', {}).get('failed_attempts', 0)
        tnt_ratio = rround(tnt_completed / (tnt_failed or 1), 2)
        return f'{tnt_completed:,}', f'{tnt_failed:,}', f'{tnt_ratio:,}'


    def get_mlg_stats(self):
        mlg_completed = self.practice_stats.get('mlg', {}).get('successful_attempts', 0)
        mlg_failed = self.practice_stats.get('mlg', {}).get('failed_attempts', 0)
        mlg_ratio = rround(mlg_completed / (mlg_failed or 1), 2)
        return f'{mlg_completed:,}', f'{mlg_failed:,}', f'{mlg_ratio:,}'


    def get_pearl_stats(self):
        pearl_completed = self.practice_stats.get('pearl_clutching', {}).get('successful_attempts', 0)
        pearl_failed = self.practice_stats.get('pearl_clutching', {}).get('failed_attempts', 0)
        pearl_ratio = rround(pearl_completed / (pearl_failed or 1), 2)
        return f'{pearl_completed:,}', f'{pearl_failed:,}', f'{pearl_ratio:,}'


    def get_blocks_placed(self):
        bridging_blocks = self.practice_stats.get('bridging', {}).get('blocks_placed', 0)
        tnt_blocks = self.practice_stats.get('fireball_jumping', {}).get('blocks_placed', 0)
        mlg_blocks = self.practice_stats.get('mlg', {}).get('blocks_placed', 0)
        blocks_placed = bridging_blocks + tnt_blocks + mlg_blocks
        return f'{blocks_placed:,}'


    def get_straight_times(self):
        short = self.practice_stats.get('records', {}).get('bridging_distance_30:elevation_NONE:angle_STRAIGHT:', 0) / 1000
        medium = self.practice_stats.get('records', {}).get('bridging_distance_50:elevation_NONE:angle_STRAIGHT:', 0) / 1000
        long = self.practice_stats.get('records', {}).get('bridging_distance_100:elevation_NONE:angle_STRAIGHT:', 0) / 1000

        total_distance = 0; output = []
        value_map = {0: 30, 1: 50, 2: 100}
        values = (short, medium, long)

        for i, value in enumerate(values):
            if value == 0: output.append('N/A')
            else:
                total_distance += value_map.get(i)
                output.append(f'{round(value, 2):,}s')

        try: average = f'{round(total_distance / (short + medium + long), 2):,}m/s'
        except ZeroDivisionError: average = 'N/A'

        return output[0], output[1], output[2], average


    def get_diagonal_times(self):
        short = self.practice_stats.get('records', {}).get('bridging_distance_30:elevation_NONE:angle_DIAGONAL:', 0) / 1000
        medium = self.practice_stats.get('records', {}).get('bridging_distance_50:elevation_NONE:angle_DIAGONAL:', 0) / 1000
        long = self.practice_stats.get('records', {}).get('bridging_distance_100:elevation_NONE:angle_DIAGONAL:', 0) / 1000

        total_distance = 0; output = []
        value_map = {0: 30, 1: 50, 2: 100}
        values = (short, medium, long)

        for i, value in enumerate(values):
            if value == 0: output.append('N/A')
            else:
                total_distance += value_map.get(i)
                output.append(f'{round(value, 2):,}s')

        try: average = f'{round(total_distance / (short + medium + long), 2):,}m/s'
        except ZeroDivisionError: average = 'N/A'

        return output[0], output[1], output[2], average
