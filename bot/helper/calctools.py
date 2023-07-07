"""
A set of functions used for calculating and fetching an assortment of data.
"""


def get_player_dict(hypixel_data: dict):
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
    :param hypixel_data_bedwars: Bedwars data stemming from player > stats > Bedwars
    """
    solos: int = hypixel_data_bedwars.get('eight_one_games_played_bedwars', 0)
    doubles: int = hypixel_data_bedwars.get('eight_two_games_played_bedwars', 0)
    threes: int = hypixel_data_bedwars.get('four_three_games_played_bedwars', 0)
    fours: int = hypixel_data_bedwars.get('four_four_games_played_bedwars', 0)
    four_vs_four: int = hypixel_data_bedwars.get('two_four_games_played_bedwars', 0)
    modes_dict: dict = {
        'Solos': solos,
        'Doubles': doubles,
        'Threes':  threes,
        'Fours': fours,
        '4v4': four_vs_four
    }
    return "N/A" if max(modes_dict.values()) == 0 else str(max(modes_dict, key=modes_dict.get))


def get_player_rank_info(hypixel_data: dict) -> dict:
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


# Suffixes used to approximate large numbers
suffixes = {
    10**60: 'NoDc', 10**57: 'OcDc', 10**54: 'SpDc', 10**51: 'SxDc', 10**48: 'QiDc', 10**45: 'QaDc',
    10**42: 'TDc', 10**39: 'DDc', 10**36: 'UDc', 10**33: 'Dc', 10**30: 'No', 10**27: 'Oc', 10**24: 'Sp',
    10**21: 'Sx', 10**18: 'Qi', 10**15: 'Qa', 10**12: 'T', 10**9: 'B', 10**6: 'M'
}


def add_suffixes(*args) -> list:
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
    modes: dict = {
        "Solos": "eight_one_",
        "Doubles": "eight_two_",
        "Threes": "four_three_",
        "Fours": "four_four_",
        "4v4": "two_four_"
    }
    return modes.get(mode, "")


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
