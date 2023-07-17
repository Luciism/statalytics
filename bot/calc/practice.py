from statalib.calctools import (
    get_rank_info,
    get_progress,
    rround,
    get_level,
    get_player_dict
)


class Practice:
    def __init__(self, name: str, hypixel_data: dict) -> None:
        self.name = name

        self.hypixel_data = get_player_dict(hypixel_data)
        self.practice_stats = self.hypixel_data.get('stats', {}).get('Bedwars', {}).get('practice', {})

        self.level = int(get_level(
            self.hypixel_data.get('stats', {}).get('Bedwars', {}).get('Experience', 0)))

        self.rank_info = get_rank_info(self.hypixel_data)
        self.progress = get_progress(self.hypixel_data.get('stats', {}).get('Bedwars', {}))


    def _calc_general_stats(self, mode):
        completed = self.practice_stats.get(mode, {}).get('successful_attempts', 0)
        failed = self.practice_stats.get(mode, {}).get('failed_attempts', 0)
        ratio = rround(completed / (failed or 1), 2)
        return f'{completed:,}', f'{failed:,}', f'{ratio:,}'


    def get_bridging_stats(self):
        return self._calc_general_stats(mode='bridging')


    def get_tnt_stats(self):
        return self._calc_general_stats(mode='fireball_jumping')


    def get_mlg_stats(self):
        return self._calc_general_stats(mode='mlg')


    def get_pearl_stats(self):
        return self._calc_general_stats(mode='pearl_clutching')


    def get_blocks_placed(self):
        bridging_blocks = self.practice_stats.get('bridging', {}).get('blocks_placed', 0)
        tnt_blocks = self.practice_stats.get('fireball_jumping', {}).get('blocks_placed', 0)
        mlg_blocks = self.practice_stats.get('mlg', {}).get('blocks_placed', 0)
        blocks_placed = bridging_blocks + tnt_blocks + mlg_blocks
        return f'{blocks_placed:,}'


    def _calc_times(self, short_key, medium_key, long_key):
        short = self.practice_stats.get('records', {}).get(short_key, 0) / 1000
        medium = self.practice_stats.get('records', {}).get(medium_key, 0) / 1000
        long = self.practice_stats.get('records', {}).get(long_key, 0) / 1000

        total_distance, output = 0, []
        value_map = {0: 30, 1: 50, 2: 100}
        values = (short, medium, long)

        for i, value in enumerate(values):
            if value == 0:
                output.append('N/A')
            else:
                total_distance += value_map.get(i)
                output.append(f'{round(value, 2):,}s')

        try:
            average = f'{round(total_distance / (short + medium + long), 2):,}m/s'
        except ZeroDivisionError:
            average = 'N/A'

        return output[0], output[1], output[2], average


    def get_straight_times(self):
        return self._calc_times(
            short_key='bridging_distance_30:elevation_NONE:angle_STRAIGHT:',
            medium_key='bridging_distance_50:elevation_NONE:angle_STRAIGHT:',
            long_key='bridging_distance_100:elevation_NONE:angle_STRAIGHT:'
        )


    def get_diagonal_times(self):
        return self._calc_times(
            short_key='bridging_distance_30:elevation_NONE:angle_DIAGONAL:',
            medium_key='bridging_distance_50:elevation_NONE:angle_DIAGONAL:',
            long_key='bridging_distance_100:elevation_NONE:angle_DIAGONAL:'
        )
