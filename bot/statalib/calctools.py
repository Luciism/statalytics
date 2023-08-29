"""
A set of functions used for calculating and fetching an assortment of data.
"""
from datetime import datetime, timedelta


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


wins_xp_map = {
    "eight_one_wins_bedwars": 100,
    "eight_two_wins_bedwars": 100,
    "four_three_wins_bedwars": 50,
    "four_four_wins_bedwars": 50,
    "two_four_wins_bedwars": 25,
    "eight_two_voidless_wins_bedwars": 50,
    "four_four_voidless_wins_bedwars": 25,
    "eight_two_rush_wins_bedwars": 50,
    "four_four_rush_wins_bedwars": 25,
    "eight_two_ultimate_wins_bedwars": 50,
    "four_four_ultimate_wins_bedwars": 25,
    "eight_two_armed_wins_bedwars": 50,
    "four_four_armed_wins_bedwars": 25,
    "eight_two_lucky_wins_bedwars": 50,
    "four_four_lucky_wins_bedwars": 25,
    "eight_two_swap_wins_bedwars": 50,
    "four_four_swap_wins_bedwars": 25,
    "eight_two_underworld_wins_bedwars": 50,
    "four_four_underworld_wins_bedwars": 25,
    "castle_wins_bedwars": 50,
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


def get_most_mode(bedwars_data: dict, key_ending: str):
    """
    Get the top mode for a certain bedwars stat
    :param bedwars_data: Hypixel bedwars data from player > stats > Bedwars
    :param key_ending: the ending of the key for the stat for example
    `games_played_bedwars`, the mode will be automatically be used for
    example `eight_one_{key_ending}`
    """
    modes_dict: dict = {
        'Solos': bedwars_data.get(f'eight_one_{key_ending}', 0),
        'Doubles': bedwars_data.get(f'eight_two_{key_ending}', 0),
        'Threes':  bedwars_data.get(f'four_three_{key_ending}', 0),
        'Fours': bedwars_data.get(f'four_four_{key_ending}', 0),
        '4v4': bedwars_data.get(f'two_four_{key_ending}', 0)
    }
    if max(modes_dict.values()) == 0:
        return "N/A"
    return str(max(modes_dict, key=modes_dict.get))


def get_most_played(bedwars_data: dict) -> str:
    """
    Gets most played bedwars modes (solos, doubles, etc)
    :param bedwars_data: Hypixel bedwars data from `player > stats > Bedwars`
    """
    return get_most_mode(bedwars_data, 'games_played_bedwars')


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


def get_progress(bedwars_data: dict) -> tuple[str, str, int]:
    """
    Get xp progress information: progress, target, and progress out of 10
    :param bedwars_data: Bedwars data stemming from player > stats > Bedwars
    """
    bedwars_level: float | int = get_level(bedwars_data.get('Experience', 0))

    remainder: int = int(str(int(bedwars_level) / 100).split(".")[-1])
    remainder_map: dict = {0: 500, 1: 1000, 2: 2000, 3: 3500}

    target: int = remainder_map.get(remainder, 5000)
    progress: float = float('.' + str(bedwars_level).split('.')[-1]) * target
    devide_by = target / 10
    progress_out_of_ten = round(progress / devide_by)

    return f'{int(progress):,}', f'{int(target):,}', progress_out_of_ten


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



def add_suffixes(*args) -> list[str] | str:
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
            value: str = f"{rround(value, 2):,}"
        formatted_values.append(value)
    if len(formatted_values) == 1:
        return formatted_values[0]
    return formatted_values


def get_mode(mode: str) -> str:
    """
    Convert a mode (Solos, Doubles, etc) into hypixel format (eight_one_, eight_two_)
    If the mode doesnt exist, returns an empty string. Used to prefix stats
    eg: f'{mode}final_kills_bedwars'
    :param mode: The mode to convert
    """
    return bedwars_modes_map.get(mode.lower(), "")


def get_wins_xp(bedwars_data: dict):
    """
    Finds the total amount of xp a player has been awarded
    by winning bedwars games accounting for different modes
    :param bedwars_data: the bedwars data json of the player
    """
    exp_data = {'experience': 0}

    for mode, exp_amount in wins_xp_map.items():
        total_wins = bedwars_data.get(mode, 0)

        mode_exp = total_wins * exp_amount

        exp_data[mode] = mode_exp
        exp_data['experience'] += mode_exp

    return exp_data


def get_quests_data(hypixel_data: dict):
    """
    Returns the completions and xp gained for each quest
    :param hypixel_data: the hypixel data for the player
    """
    total_experience = hypixel_data.get(
        'stats', {}).get('Bedwars', {}).get('Experience', 0)

    quest_data = {'quests_exp': {}, 'completions': 0}
    xp_by_quests = 0

    for quest, exp in quest_xp_map.items():
        if isinstance(exp, dict):
            quest_completions: list[dict] = hypixel_data.get(
                'quests', {}).get(quest, {}).get('completions', {})

            quest_data['completions'] += len(quest_completions)

            quest_exp = 0
            for completion in quest_completions:
                completed_timestamp = completion.get('time', 0)

                for timestamp, timestamp_exp in exp.items():
                    if completed_timestamp >= timestamp:
                        quest_exp += timestamp_exp

            xp_by_quests += quest_exp
            quest_data['quests_exp'].setdefault(
                quest, {})['completions'] = len(quest_completions)
            quest_data['quests_exp'][quest]['experience'] = quest_exp

        else:
            completions = len(hypixel_data.get(
                'quests', {}).get(quest, {}).get('completions', {}))

            quest_exp = completions * exp
            xp_by_quests += quest_exp

            quest_data['quests_exp'].setdefault(quest, {})['completions'] = completions
            quest_data['quests_exp'][quest]['experience'] = quest_exp
            quest_data['completions'] += completions

    quest_data['real_exp'] = total_experience - xp_by_quests
    quest_data['total_quests_exp'] = xp_by_quests

    return quest_data


def ratio(dividend: int, divisor: int) -> int | float:
    """
    Safely gets the ratio of 2 numbers nicely rounded to
    2 decimal places.
    :param dividend: the dividend in the division
    :param divisor: the divisor in the division
    """
    return rround(dividend / (divisor or 1), 2)


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

        self.title_mode = real_title_case(strict_mode or 'overall')

        self.wins = self._get_mode_stats('wins_bedwars')
        self.losses = self._get_mode_stats('losses_bedwars')
        self.wlr = self._get_ratio(self.wins, self.losses)

        self.final_kills = self._get_mode_stats('final_kills_bedwars')
        self.final_deaths = self._get_mode_stats('final_deaths_bedwars')
        self.fkdr = self._get_ratio(self.final_kills, self.final_deaths)

        self.beds_broken = self._get_mode_stats('beds_broken_bedwars')
        self.beds_lost = self._get_mode_stats('beds_lost_bedwars')
        self.bblr = self._get_ratio(self.beds_broken, self.beds_lost)

        self.kills = self._get_mode_stats('kills_bedwars')
        self.deaths = self._get_mode_stats('deaths_bedwars')
        self.kdr = self._get_ratio(self.kills, self.deaths)

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

        self.winstreak = self._bedwars_data.get('winstreak')
        if self.winstreak is not None:
            self.winstreak_str = f'{self.winstreak:,}'
        else:
            self.winstreak_str = 'API Off'
            self.winstreak = 0

        self._quests_data = None

        self._wins_xp_data = None
        self._wins_xp = None


    @property
    def quests_data(self):
        if self._quests_data is None:
            self._quests_data = get_quests_data(self._hypixel_data)
        return self._quests_data

    @property
    def questless_exp(self):
        return self.quests_data.get('real_exp', 0)

    @property
    def wins_xp_data(self):
        if self._wins_xp_data is None:
            self._wins_xp_data = get_wins_xp(self._bedwars_data)
        return self._wins_xp_data

    @property
    def wins_xp(self):
        return self.wins_xp_data.get('experience', 0)


    def _get_ratio(self, val_1: int, val_2: int):
        if isinstance(val_1, dict):
            ratios = {}

            for key, value in val_1.items():
                ratios[key] = rround(value / (val_2[key] or 1), 2)
            return ratios

        return rround(val_1 / (val_2 or 1), 2)


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
        strict_mode: str='overall'
    ) -> None:
        """
        :param hypixel_data: the raw hypixel response json
        :param local_bedwars_data: locally stored snapshot of a player's stats
        :param strict_mode: the mode to fetch stats for (overall, solos, doubles, etc)
        """
        super().__init__(hypixel_data, strict_mode)

        self._local_bedwars_data = local_bedwars_data

        self.wins_local = self._get_mode_stats_local('wins_bedwars')
        self.losses_local = self._get_mode_stats_local('losses_bedwars')

        self.wins_cum = self._calc_cum('wins_bedwars')
        self.losses_cum = self._calc_cum('losses_bedwars')
        self.wlr_cum = self._get_ratio(self.wins_cum, self.losses_cum)

        self.final_kills_local = self._get_mode_stats_local('final_kills_bedwars')
        self.final_deaths_local = self._get_mode_stats_local('final_deaths_bedwars')

        self.final_kills_cum = self._calc_cum('final_kills_bedwars')
        self.final_deaths_cum = self._calc_cum('final_deaths_bedwars')
        self.fkdr_cum = self._get_ratio(self.final_kills_cum, self.final_deaths_cum)

        self.beds_broken_local = self._get_mode_stats_local('beds_broken_bedwars')
        self.beds_lost_local = self._get_mode_stats_local('beds_lost_bedwars')

        self.beds_broken_cum = self._calc_cum('beds_broken_bedwars')
        self.beds_lost_cum = self._calc_cum('beds_lost_bedwars')
        self.bblr_cum = self._get_ratio(self.beds_broken_cum, self.beds_lost_cum)

        self.kills_local = self._get_mode_stats_local('kills_bedwars')
        self.deaths_local = self._get_mode_stats_local('deaths_bedwars')

        self.kills_cum = self._calc_cum('kills_bedwars')
        self.deaths_cum = self._calc_cum('deaths_bedwars')
        self.kdr_cum = self._get_ratio(self.kills_cum, self.deaths_cum)

        self.most_played_cum = self._get_most_played()
        self.games_played_cum = self._calc_cum('games_played_bedwars')

        self.experience_local = self._local_bedwars_data.get(f'Experience', 0)
        self.level_local = get_level(self.experience_local)

        self.experience_cum = self.experience - self.experience_local
        self.levels_cum = self.level - get_level(self.experience_local)

        self.items_purchased_cum = self._calc_cum('items_purchased_bedwars')


    def _get_mode_stats_local(self, key: str, default=0) -> dict | int:
        if self._strict_mode is None:
            mode_stats = {}
            for mode, prefix in bedwars_modes_map.items():
                mode_stats[mode] = self._local_bedwars_data.get(
                    f'{prefix}{key}', default)
            return mode_stats

        prefix = bedwars_modes_map.get(self._strict_mode.lower())
        return self._local_bedwars_data.get(f'{prefix}{key}', default)


    def _calc_cum(self, key: str) -> int:
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


class ProjectedStats(CumulativeStats):
    def __init__(
        self,
        hypixel_data: dict,
        session_bedwars_data: dict,
        target_level: float=None,
        target_date: datetime=None,
        strict_mode: str='overall'
    ):
        """
        #### Either `target_level` or `target_date` must be provided but only one
        :param hypixel_data: the raw hypixel response json
        :param session_bedwars_data: locally stored snapshot of a player's stats
        :param target_level: the level to predict stats for
        :param target_date: the date to predict the stats for
        :param strict_mode: the mode to fetch stats for (overall, solos, doubles, etc)
        """
        # Ensure either target_level or target_date was provided
        assert (target_level, target_date).count(None) == 1

        super().__init__(hypixel_data, session_bedwars_data, strict_mode)

        now = datetime.now()

        session_start_time = datetime.strptime(
            session_bedwars_data['date'], "%Y-%m-%d")
        self.session_duration_days = (now - session_start_time).days

        self.levels_per_day = ratio(self.levels_cum, self.session_duration_days)

        if target_level is None:
            self.days_to_go = (target_date - now).days or 1

            target_level = self.level + (self.levels_per_day * self.days_to_go)
            self.levels_to_go = target_level - self.level
        else:
            self.levels_to_go = target_level - self.level
            days_per_level_gained = (self.session_duration_days / (self.levels_cum or 1))

            self.days_to_go = int(days_per_level_gained * self.levels_to_go)

            try:
                target_date = now + timedelta(days=self.days_to_go)
            except OverflowError:
                target_date = None

        self.target_level = target_level
        self.target_date = target_date

        self.complete_percent = f"{round((self.level / (target_level or 1)) * 100, 2)}%"


        self.wins_projected = self._calc_projection(
            self.wins, self.wins_cum, increase=True)

        self.losses_projected = self._calc_projection(
            self.losses, self.losses_cum)

        self.wlr_projected = ratio(
            self.wins_projected, self.losses_projected)


        self.final_kills_projected = self._calc_projection(
            self.final_kills, self.final_kills_cum, increase=True)

        self.final_deaths_projected = self._calc_projection(
            self.final_deaths, self.final_deaths_cum)

        self.fkdr_projected = ratio(
            self.final_kills_projected, self.final_deaths_projected)


        self.beds_broken_projected = self._calc_projection(
            self.beds_broken, self.beds_broken_cum, increase=True)

        self.beds_lost_projected = self._calc_projection(
            self.beds_lost, self.beds_lost_cum)

        self.bblr_projected = ratio(
            self.beds_broken_projected, self.beds_lost_projected)


        self.kills_projected = self._calc_projection(
            self.kills, self.kills_cum, increase=True)

        self.deaths_projected = self._calc_projection(
            self.deaths, self.deaths_cum)

        self.kdr_projected = ratio(
            self.kills_projected, self.deaths_projected)


        self.items_purchased_projected = self._calc_projection(
                self.items_purchased, self.items_purchased_cum)

        self.wins_per_star = self._per_star(self.wins_projected, self.wins)
        self.kills_per_star = self._per_star(self.kills_projected, self.kills)

        self.final_kills_per_star = self._per_star(
            self.final_kills_projected, self.final_kills)

        self.beds_broken_per_star = self._per_star(
            self.beds_broken_projected, self.beds_broken)

        self._projection_date: str = None


    @property
    def projection_date(self):
        """Projected date formatted as `%b %d, %Y`"""
        if self._projection_date is None:
            if self.target_date is None:
                self._projection_date =  "Deceased"
            else:
                self._projection_date = self.target_date.strftime("%b %d, %Y")
        return self._projection_date


    def _per_star(self, projected_value: int, current_value: int):
        per_star = (projected_value - current_value) / (self.levels_to_go or 1)
        return rround(per_star, 2)


    def _calc_projection(self, current_value: int, cum_value: int, increase=True):
        value_per_day = cum_value / (self.session_duration_days or 1)
        added_value = value_per_day * self.days_to_go

        projected_value = current_value + added_value

        # Account for 0.02% skill increase per star gained
        if increase:
            projected_value += projected_value * 0.0002 * self.levels_to_go

        return int(projected_value)
