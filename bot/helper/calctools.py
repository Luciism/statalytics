def get_most_played(hypixel_data_bedwars):
    solos = hypixel_data_bedwars.get('eight_one_games_played_bedwars', 0)
    doubles = hypixel_data_bedwars.get('eight_two_games_played_bedwars', 0)
    threes = hypixel_data_bedwars.get('four_three_games_played_bedwars', 0)
    fours = hypixel_data_bedwars.get('four_four_games_played_bedwars', 0)
    findgreatest = {
        'Solos': solos,
        'Doubles': doubles,
        'Threes':  threes,
        'Fours': fours
    }
    return "N/A" if max(findgreatest.values()) == 0 else str(max(findgreatest, key=findgreatest.get))


def get_player_rank_info(hypixel_data):
    name = hypixel_data.get('displayname')
    rank_info = {
        'rank': hypixel_data.get('rank', 'NONE') if name != "Technoblade" else "TECHNO",
        'packageRank': hypixel_data.get('packageRank', 'NONE'),
        'newPackageRank': hypixel_data.get('newPackageRank', 'NONE'),
        'monthlyPackageRank': hypixel_data.get('monthlyPackageRank', 'NONE'),
        'rankPlusColor': hypixel_data.get('rankPlusColor', None) if name != "Technoblade" else "AQUA"
    }
    return rank_info


def get_level(xp):
    level = 100 * (xp // 487000)  # prestige
    xp %= 487000  # exp this prestige
    xp_map = (0, 500, 1500, 3500, 7000)

    for index, value in enumerate(xp_map):
        if xp < value:
            factor = xp_map[index-1]
            return level + ((xp - factor) / (value - factor)) + (index - 1)
    return level + (xp - 7000) / 5000 + 4


def get_progress(hypixel_data_bedwars):
    bedwars_level = get_level(hypixel_data_bedwars.get('Experience', 0))

    remainder = int(str(int(bedwars_level) / 100).split(".")[-1])
    remainder_map = {0: 500, 1: 1000, 2: 2000, 3: 3500}

    target = remainder_map.get(remainder, 5000)
    progress = float('.' + str(bedwars_level).split('.')[-1]) * target
    devide_by = target / 10
    progress_out_of_ten = round(progress / devide_by)

    return f'{int(progress):,}', f'{int(target):,}', progress_out_of_ten


global suffixes
suffixes = {
    10**60: 'NoDc', 10**57: 'OcDc', 10**54: 'SpDc', 10**51: 'SxDc', 10**48: 'QiDc', 10**45: 'QaDc',
    10**42: 'TDc', 10**39: 'DDc', 10**36: 'UDc', 10**33: 'Dc', 10**30: 'No', 10**27: 'Oc', 10**24: 'Sp',
    10**21: 'Sx', 10**18: 'Qi', 10**15: 'Qa', 10**12: 'T', 10**9: 'B', 10**6: 'M'
}


def add_suffixes(*args):
    formatted_values = []
    for value in args:
        for num, suffix in suffixes.items():
            if value >= num:
                value = f"{value/num:,.1f}{suffix}"
                break
        else:
            value = f"{value:,}"
        formatted_values.append(value)
    return formatted_values


def get_mode(mode: str) -> str:
    modes = {
        "Solos": "eight_one_",
        "Doubles": "eight_two_",
        "Threes": "four_three_",
        "Fours": "four_four_",
        "4v4": "two_four_"
    }
    return modes.get(mode, "")

def rround(number: float | int, ndigits: int=0) -> float | int:
    rounded: float = float(round(number, ndigits))
    if rounded.is_integer(): rounded = int(rounded)
    return rounded
