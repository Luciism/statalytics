"""
A set of functions used for calculating and fetching an assortment of data.
"""

bedwars_modes_map = {
    "overall": "",
    "solos": "eight_one_",
    "doubles": "eight_two_",
    "threes": "four_three_",
    "fours": "four_four_",
    "4v4": "two_four_"
}


quest_xp_map = {
    "bedwars_daily_win": 250,
    "bedwars_daily_one_more": {
        1683085688000: 250,
        0: 0
    },
    "bedwars_daily_gifts": 700,
    "bedwars_daily_nightmares": 1000,
    "bedwars_daily_final_killer": 250,
    "bedwars_daily_bed_breaker": 250,
    "bedwars_weekly_bed_elims": 5000,
    "bedwars_weekly_dream_win": 5000,
    "bedwars_weekly_challenges": 2500,
    "bedwars_weekly_pumpkinator": 6666,
    "bedwars_weekly_challenges_win": 5000,
    "bedwars_weekly_final_killer": 5000
}

# Suffixes used to approximate large numbers
suffixes = {
    10**60: 'NoDc', 10**57: 'OcDc', 10**54: 'SpDc', 10**51: 'SxDc',
    10**48: 'QiDc', 10**45: 'QaDc', 10**42: 'TDc', 10**39: 'DDc',
    10**36: 'UDc', 10**33: 'Dc', 10**30: 'No', 10**27: 'Oc', 10**24: 'Sp',
    10**21: 'Sx', 10**18: 'Qi', 10**15: 'Qa', 10**12: 'T', 10**9: 'B', 10**6: 'M'
}


def real_title_case(text: str) -> str:
    """
    Like calling .title() except it wont capitalize words like `4v4`
    :param text: the text to turn title case
    """
    words = text.split()
    title_words = [word.title() if word[0].isalpha() else word for word in words]
    return ' '.join(title_words)


def get_player_dict(hypixel_data: dict) -> dict:
    """
    Checks if player key exits and returns data or empty dict
    :param hypixel_data: The hypixel data to the player of
    """
    if hypixel_data.get('player'):
        return hypixel_data['player']
    return {}


def get_most_played(hypixel_data_bedwars: dict) -> str:
    """
    Gets most played bedwars modes (solos, doubles, etc)
    :param hypixel_data_bedwars: Hypixel bedwars data from player > stats > Bedwars
    """
    modes_dict: dict = {
        'Solos': hypixel_data_bedwars.get('eight_one_games_played_bedwars', 0),
        'Doubles': hypixel_data_bedwars.get('eight_two_games_played_bedwars', 0),
        'Threes':  hypixel_data_bedwars.get('four_three_games_played_bedwars', 0),
        'Fours': hypixel_data_bedwars.get('four_four_games_played_bedwars', 0),
        '4v4': hypixel_data_bedwars.get('two_four_games_played_bedwars', 0)
    }
    if max(modes_dict.values()) == 0:
        return "N/A"
    return str(max(modes_dict, key=modes_dict.get))


def get_rank_info(hypixel_data: dict) -> dict:
    """
    Returns player's rank information including plus color
    :param hypixel_data: Hypixel data stemming from player key
    """
    name: str = hypixel_data.get('displayname')
    rank_info: dict = {
        'rank': hypixel_data.get('rank', 'NONE') if name != "Technoblade" else "TECHNO",
        'packageRank': hypixel_data.get('packageRank', 'NONE'),
        'newPackageRank': hypixel_data.get('newPackageRank', 'NONE'),
        'monthlyPackageRank': hypixel_data.get('monthlyPackageRank', 'NONE'),
        'rankPlusColor': hypixel_data.get('rankPlusColor', None) if name != "Technoblade" else "AQUA"
    }
    return rank_info


def xp_from_level(level: float) -> float | int:
    """
    Get the bedwars experience required for a given level
    :param level: Bedwars level
    """
    prestige, level = divmod(level, 100)
    xp = prestige * 487000
    xp_map = (0, 500, 1500, 3500, 7000)

    if level < 4:
        index = int(level)
        factor = xp_map[index]
        return int(xp + factor + (level - index) * (xp_map[index + 1] - factor))
    else:
        return int(xp + 7000 + (level - 4) * 5000)


def get_level(xp: int) -> float | int:
    """
    Get a player's precise bedwars level from their experience
    :param xp: Player's bedwars experience
    """
    level: int = 100 * (xp // 487000)  # prestige
    xp %= 487000  # exp this prestige
    xp_map: tuple = (0, 500, 1500, 3500, 7000)

    for index, value in enumerate(xp_map):
        if xp < value:
            factor: int = xp_map[index-1]
            return level + ((xp - factor) / (value - factor)) + (index - 1)
    return level + (xp - 7000) / 5000 + 4


def get_progress(hypixel_data_bedwars: dict) -> tuple[str, str, int]:
    """
    Get xp progress information: progress, target, and progress out of 10
    :param hypixel_data_bedwars: Bedwars data stemming from player > stats > Bedwars
    """
    bedwars_level: float | int = get_level(hypixel_data_bedwars.get('Experience', 0))

    remainder: int = int(str(int(bedwars_level) / 100).split(".")[-1])
    remainder_map: dict = {0: 500, 1: 1000, 2: 2000, 3: 3500}

    target: int = remainder_map.get(remainder, 5000)
    progress: float = float('.' + str(bedwars_level).split('.')[-1]) * target
    devide_by = target / 10
    progress_out_of_ten = round(progress / devide_by)

    return f'{int(progress):,}', f'{int(target):,}', progress_out_of_ten


def add_suffixes(*args) -> list[str]:
    """
    Add suffixes to the end of large numbers to approximate them
    :param *args: A list of numbers to approximate
    """
    formatted_values: list = []
    for value in args:
        for num, suffix in suffixes.items():
            if value >= num:
                value: str = f"{value/num:,.1f}{suffix}"
                break
        else:
            value: str = f"{value:,}"
        formatted_values.append(value)
    return formatted_values


def get_mode(mode: str) -> str:
    """
    Convert a mode (Solos, Doubles, etc) into hypixel format (eight_one_, eight_two_)
    If the mode doesnt exist, returns an empty string. Used to prefix stats
    eg: f'{mode}final_kills_bedwars'
    :param mode: The mode to convert
    """
    return bedwars_modes_map.get(mode.lower(), "")


def rround(number: float | int, ndigits: int=0) -> float | int:
    """
    Rounds a number. If the number is a whole number, it will be converted to an int
    :param number: Number to be round
    :param ndigits: Decimal place to round to
    """
    rounded: float = float(round(number, ndigits))
    if rounded.is_integer():
        rounded = int(rounded)
    return rounded


def get_playtime_xp(hypixel_data: dict):
    """
    Returns a player's bedwars experience gained without the use of quests
    :param hypixel_data: the hypixel data for the player
    """
    total_experience = hypixel_data.get(
        'stats', {}).get('Bedwars', {}).get('Experience', 0)

    xp_by_quests = 0

    for quest, exp in quest_xp_map.items():
        if isinstance(exp, dict):
            quest_completions: list[dict] = hypixel_data.get(
                'quests', {}).get(quest, {}).get('completions', {})

            for completion in quest_completions:
                completed_timestamp = completion.get('time', 0)

                for timestamp, timestamp_exp in exp.items():
                    if completed_timestamp >= timestamp:
                        xp_by_quests += timestamp_exp
        
        else:
            completions = len(hypixel_data.get(
                'quests', {}).get(quest, {}).get('completions', {}))
            xp_by_quests += completions * exp

    return total_experience - xp_by_quests


class BedwarsStats:
    """Wrapper for generic hypixel bedwars stats"""
    def __init__(self, hypixel_data: dict, strict_mode: str=None):
        """
        :param hypixel_data: the raw hypixel response json
        :param strict_mode: the mode to fetch stats for (solos, doubles, etc)
        if left as `None`, a dictionary of stats for every mode will be returned,
        otherwise just the stats for the specified mode will be returned
        """
        self._strict_mode = strict_mode
        self._hypixel_data = get_player_dict(hypixel_data)

        self._bedwars_data = self._hypixel_data.get('stats', {}).get('Bedwars', {})

        self.wins = self._get_mode_stats('wins_bedwars')
        self.losses = self._get_mode_stats('losses_bedwars')
        self.wlr = rround(self.wins / (self.losses or 1), 2)

        self.final_kills = self._get_mode_stats('final_kills_bedwars')
        self.final_deaths = self._get_mode_stats('final_deaths_bedwars')
        self.fkdr = rround(self.final_kills / (self.final_deaths or 1), 2)

        self.beds_broken = self._get_mode_stats('beds_broken_bedwars')
        self.beds_lost = self._get_mode_stats('beds_lost_bedwars')
        self.bblr = rround(self.beds_broken / (self.beds_lost or 1), 2)

        self.kills = self._get_mode_stats('kills_bedwars')
        self.deaths = self._get_mode_stats('deaths_bedwars')
        self.kdr = rround(self.kills / (self.deaths or 1), 2)

        self.games_played = self._get_mode_stats('games_played_bedwars')
        self.most_played = get_most_played(self._bedwars_data)

        self.experience = self._bedwars_data.get('Experience', 0)
        self.progress = get_progress(self._bedwars_data)
        self.level = get_level(self.experience)

        self.items_purchased = self._get_mode_stats('items_purchased_bedwars')
        self.tools_purchased = self._get_mode_stats('permanent_items_purchased_bedwars')

        self.resources_collected = self._get_mode_stats('resources_collected_bedwars')
        self.iron_collected = self._get_mode_stats('iron_resources_collected_bedwars')
        self.gold_collected = self._get_mode_stats('gold_resources_collected_bedwars')
        self.diamonds_collected = self._get_mode_stats('diamond_resources_collected_bedwars')
        self.emeralds_collected = self._get_mode_stats('emerald_resources_collected_bedwars')

        self.loot_chests_regular = self._bedwars_data.get('bedwars_boxes', 0)
        self.loot_chests_christmas = self._bedwars_data.get('bedwars_christmas_boxes', 0)
        self.loot_chests_easter = self._bedwars_data.get('bedwars_easter_boxes', 0)
        self.loot_chests_halloween = self._bedwars_data.get('bedwars_halloween_boxes', 0)

        self.loot_chests = int(self.loot_chests_regular + self.loot_chests_christmas
            + self.loot_chests_easter + self.loot_chests_halloween)
        
        self.coins = self._bedwars_data.get('coins', 0)

        self.winstreak = self._get_mode_stats('winstreak', default=None)
        if self.winstreak is not None:
            self.winstreak_str = f'{self.winstreak:,}'
        else:
            self.winstreak_str = 'API Off'
            self.winstreak = 0

        self._playtime_xp = None


    @property
    def playtime_xp(self):
        if self._playtime_xp is None:
            self._playtime_xp = get_playtime_xp(self._hypixel_data)
        return self._playtime_xp


    def _get_mode_stats(self, key: str, default=0) -> dict | int:
        if self._strict_mode is None:
            mode_stats = {}
            for mode, prefix in bedwars_modes_map.items():
                mode_stats[mode] = self._bedwars_data.get(f'{prefix}{key}', default)
            return mode_stats

        prefix = bedwars_modes_map.get(self._strict_mode.lower())
        return self._bedwars_data.get(f'{prefix}{key}', default)


class CumulativeStats(BedwarsStats):
    def __init__(
        self,
        hypixel_data: dict,
        local_bedwars_data: dict,
        strict_mode: str=None
    ) -> None:
        super().__init__(hypixel_data, strict_mode)

        self._local_bedwars_data = local_bedwars_data

        self.wins_cum: int = self._calc_cum('wins_bedwars')
        self.losses_cum: int = self._calc_cum('losses_bedwars')
        self.wlr_cum = rround(self.wins_cum / (self.losses_cum or 1), 2)
    
        self.final_kills_cum: int = self._calc_cum('final_kills_bedwars')
        self.final_deaths_cum: int = self._calc_cum('final_deaths_bedwars')
        self.fkdr_cum = rround(self.final_kills_cum / (self.final_deaths_cum or 1), 2)

        self.beds_broken_cum: int = self._calc_cum('beds_broken_bedwars')
        self.beds_lost_cum: int = self._calc_cum('beds_lost_bedwars')
        self.bblr_cum = rround(self.beds_broken_cum / (self.beds_lost_cum or 1), 2)

        self.kills_cum: int = self._calc_cum('kills_bedwars')
        self.deaths_cum: int = self._calc_cum('deaths_bedwars')
        self.kdr_cum = rround(self.kills_cum / (self.deaths_cum or 1), 2)

        self.most_played_cum = self._get_most_played()
        self.games_played_cum: int = self._calc_cum('games_played_bedwars')

        local_experience = self._local_bedwars_data.get(f'Experience', 0)
        self.experience_cum = self.experience - local_experience
        self.levels_cum = self.level - get_level(local_experience)

        self.items_purchased_cum: int = self._calc_cum('items_purchased_bedwars')


    def _get_mode_stats_local(self, key: str, default=0) -> dict | int:
        if self._strict_mode is None:
            mode_stats = {}
            for mode, prefix in bedwars_modes_map.items():
                mode_stats[mode] = self._local_bedwars_data.get(
                    f'{prefix}{key}', default)
            return mode_stats

        prefix = bedwars_modes_map.get(self._strict_mode.lower())
        return self._local_bedwars_data.get(f'{prefix}{key}', default)


    def _calc_cum(self, key: str):
        hypixel_value = self._get_mode_stats(key)
        local_value = self._get_mode_stats_local(key)

        return hypixel_value - local_value


    def _get_most_played(self):
        modes_dict = {
            'Solos': self._calc_cum('eight_one_games_played_bedwars'),
            'Doubles': self._calc_cum('eight_two_games_played_bedwars'),
            'Threes': self._calc_cum('four_three_games_played_bedwars'),
            'Fours': self._calc_cum('four_four_games_played_bedwars'),
            '4v4': self._calc_cum('two_four_games_played_bedwars')
        }
        if max(modes_dict.values()) == 0:
            return "N/A"
        return str(max(modes_dict, key=modes_dict.get))
