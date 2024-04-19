from statalib.calctools import BedwarsStats, get_rank_info, ratio


class PracticeStats(BedwarsStats):
    def __init__(
        self,
        hypixel_data: dict
    ) -> None:
        super().__init__(hypixel_data, strict_mode='overall')
        self.practice_stats: dict = self._bedwars_data.get('practice', {})

        self.level = int(self.level)
        self.rank_info = get_rank_info(self._hypixel_data)

        self.bridging_completed = self._get_successes('bridging')
        self.bridging_failed = self._get_fails('bridging')
        self.bridging_ratio = ratio(self.bridging_completed, self.bridging_failed)

        self.tnt_completed = self._get_successes('fireball_jumping')
        self.tnt_failed = self._get_fails('fireball_jumping')
        self.tnt_ratio = ratio(self.tnt_completed, self.tnt_failed)

        self.mlg_completed = self._get_successes('mlg')
        self.mlg_failed = self._get_fails('mlg')
        self.mlg_ratio = ratio(self.mlg_completed, self.mlg_failed)

        self.pearl_completed = self._get_successes('pearl_clutching')
        self.pearl_failed = self._get_fails('pearl_clutching')
        self.pearl_ratio = ratio(self.pearl_completed, self.pearl_failed)

        self.straight_short_record = self._pretty_record('30', 'NONE', 'STRAIGHT')
        self.straight_medium_record = self._pretty_record('50', 'NONE', 'STRAIGHT')
        self.straight_long_record = self._pretty_record('100', 'NONE', 'STRAIGHT')
        self.straight_average_time = self._average_time('STRAIGHT')

        self.diagonal_short_record = self._pretty_record('30', 'NONE', 'DIAGONAL')
        self.diagonal_medium_record = self._pretty_record('50', 'NONE', 'DIAGONAL')
        self.diagonal_long_record = self._pretty_record('100', 'NONE', 'DIAGONAL')
        self.diagonal_average_time = self._average_time('DIAGONAL')

        self._blocks_placed = None
        self._total_attempts = None


    @property
    def blocks_placed(self):
        if self._blocks_placed is None:
            bridging_blocks = self.practice_stats.get('bridging', {}).get('blocks_placed', 0)
            tnt_blocks = self.practice_stats.get('fireball_jumping', {}).get('blocks_placed', 0)
            mlg_blocks = self.practice_stats.get('mlg', {}).get('blocks_placed', 0)
            self._blocks_placed = bridging_blocks + tnt_blocks + mlg_blocks
        return self._blocks_placed


    @property
    def total_attempts(self):
        if self._total_attempts is None:
            self._total_attempts = sum((
                self.bridging_completed, self.bridging_failed,
                self.tnt_completed, self.tnt_failed, self.mlg_completed,
                self.mlg_failed, self.pearl_completed, self.pearl_failed
            ))
        return self._total_attempts


    def _get_successes(self, mode: str):
        return self.practice_stats.get(mode, {}).get('successful_attempts', 0)


    def _get_fails(self, mode: str):
        return self.practice_stats.get(mode, {}).get('failed_attempts', 0)


    def _record(self, distance: str, elevation: str, angle: str):
        key = f"bridging_distance_{distance}:elevation_{elevation}:angle_{angle}:"
        return self.practice_stats.get('records', {}).get(key, 0) / 1000


    def _pretty_record(self, distance: str, elevation: str, angle: str):
        record = self._record(distance, elevation, angle)

        if record == 0:
            return 'N/A'
        return f'{round(record, 2):,}s'


    def _average_time(self, angle: str):
        short = self._record('30', 'NONE', angle)
        medium = self._record('50', 'NONE', angle)
        long = self._record('100', 'NONE', angle)

        total_distance = 0
        distance_map = (30, 50, 100)

        for i, time in enumerate((short, medium, long)):
            if time != 0:
                total_distance += distance_map[i]

        total_time = (short + medium + long)
        if total_time == 0:
            return 'N/A'
        return f'{round(total_distance / total_time, 2):,}m/s'
