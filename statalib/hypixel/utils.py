from typing import TypedDict, NamedTuple


PROGRESS_BAR_MAX = 30

BEDWARS_MODES_MAP = {
    "overall": "",
    "solos": "eight_one_",
    "doubles": "eight_two_",
    "threes": "four_three_",
    "fours": "four_four_",
    "4v4": "two_four_"
}

WINS_XP_MAP = {
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
NUM_SUFFIXES_MAP = {
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
    Checks if player key exists and returns data or empty dict
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


def get_mode(mode: str) -> str:
    """
    Convert a mode (Solos, Doubles, etc) into hypixel format (eight_one_, eight_two_)
    If the mode doesnt exist, returns an empty string. Used to prefix stats
    eg: f'{mode}final_kills_bedwars'
    :param mode: The mode to convert
    """
    return BEDWARS_MODES_MAP.get(mode.lower(), "")


def calc_xp_from_wins(bedwars_data: dict):
    """
    Finds the total amount of xp a player has been awarded
    by winning bedwars games accounting for different modes
    :param bedwars_data: the bedwars data json of the player
    """
    exp_data = {'experience': 0}

    for mode, exp_amount in WINS_XP_MAP.items():
        total_wins = bedwars_data.get(mode, 0)

        mode_exp = total_wins * exp_amount

        exp_data[mode] = mode_exp
        exp_data['experience'] += mode_exp

    return exp_data


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
        for num, suffix in NUM_SUFFIXES_MAP.items():
            if value >= num:
                value: str = f"{value/num:,.1f}{suffix}"
                break
        else:
            value: str = f"{rround(value, 2):,}"
        formatted_values.append(value)
    if len(formatted_values) == 1:
        return formatted_values[0]
    return formatted_values


def ratio(dividend: int, divisor: int) -> int | float:
    """
    Safely gets the ratio of 2 numbers nicely rounded to
    2 decimal places.
    :param dividend: the dividend in the division
    :param divisor: the divisor in the division
    """
    return rround(dividend / (divisor or 1), 2)
