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


def decimal_of(number: float):
    """
    Returns the decimal on the right side of the . for a float
    for example `1.521` would return `521`
    :param number: the floating point number to get the decimal of
    """
    return int(str(number).split(".")[-1])


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


def get_progress(experience: int) -> tuple[str, str, int]:
    """
    Get the leveling progress information from bedwars experience
    :param experience: the bedwars experience to get the level progress of
    :param return: (level xp progress, level xp target, level xp progress of 10)
    """
    level: float = get_level(experience)

    # levels gained this prestige
    lvls_since_pres = level % 100

    # target xp for getting to next level based on levels gained
    # this current prestige. for `0` it would be `500` xp for the next level
    # `1` would be `1000` xp, etc, otherwise if it is above `3`, it will always
    # be `5000` xp
    level_xp_map: dict = {0: 500, 1: 1000, 2: 2000, 3: 3500}
    target_xp: int = level_xp_map.get(int(lvls_since_pres), 5000)

    lvl_progress = float(f'.{decimal_of(level)}') * target_xp
    devide_by = target_xp / 10
    progress_out_of_ten = round(lvl_progress / devide_by)

    return f'{int(lvl_progress):,}', f'{int(target_xp):,}', progress_out_of_ten


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