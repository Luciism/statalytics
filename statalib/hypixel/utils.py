"""Utility functions for calculating bedwars stats."""

from typing import Literal
from typing_extensions import deprecated

from ..aliases import BedwarsData, HypixelData, HypixelPlayerData
from ..common import Mode, ModesEnum

PROGRESS_BAR_MAX = 30
"Maximum progress bar length."

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
"Mode name to win xp amount mapping."

# Suffixes used to approximate large numbers
NUM_SUFFIXES_MAP = {
    10**60: "NoDc",
    10**57: "OcDc",
    10**54: "SpDc",
    10**51: "SxDc",
    10**48: "QiDc",
    10**45: "QaDc",
    10**42: "TDc",
    10**39: "DDc",
    10**36: "UDc",
    10**33: "Dc",
    10**30: "No",
    10**27: "Oc",
    10**24: "Sp",
    10**21: "Sx",
    10**18: "Qi",
    10**15: "Qa",
    10**12: "T",
    10**9: "B",
    10**6: "M",
}


def get_player_dict(hypixel_data: HypixelData) -> HypixelPlayerData:
    """
    Check if player key exists and returns data or empty dict.

    :param hypixel_data: The raw Hypixel API JSON response.
    """
    return hypixel_data.get("player") or {}


def get_most_mode_v2(
    bedwars_data: BedwarsData, stat_key: str, dreams: bool = False
) -> Mode | None:
    """
    Return the mode with the most amount of a certain statistic.

    :param bedwars_data: Hypixel bedwars data from 'player'>'stats'>'Bedwars'.
    :param stat_key: The bedwars stat key, for example `games_played_bedwars`.
    """
    modes = ModesEnum.non_dream_modes() if not dreams else ModesEnum.dream_modes()

    mode_tuples = [
        (mode, bedwars_data.get(f"{mode.prefix}{stat_key}", 0))
        for mode in modes
        if mode.is_real
    ]

    if max(mode_tuples, key=lambda m: m[1]) == 0:
        return None

    return max(mode_tuples, key=lambda m: m[1])[0]


@deprecated("Use get_most_mode_v2 instead")
def get_most_mode(
    bedwars_data: BedwarsData, stat_key: str
) -> Literal["Solos", "Doubles", "Threes", "Fours", "4v4", "N/A"]:
    """
    Return the mode with the most amount of a certain statistic.

    :param bedwars_data: Hypixel bedwars data from 'player'>'stats'>'Bedwars'.
    :param stat_key: The bedwars stat key, for example `games_played_bedwars`.
    """
    modes_dict: dict[str, int] = {
        "Solos": bedwars_data.get(f"eight_one_{stat_key}", 0),
        "Doubles": bedwars_data.get(f"eight_two_{stat_key}", 0),
        "Threes": bedwars_data.get(f"four_three_{stat_key}", 0),
        "Fours": bedwars_data.get(f"four_four_{stat_key}", 0),
        "4v4": bedwars_data.get(f"two_four_{stat_key}", 0),
    }
    if max(modes_dict.values()) == 0:
        return "N/A"
    return str(max(modes_dict, key=modes_dict.get))


def get_most_played_mode(
    bedwars_data: BedwarsData, dreams: bool = False
) -> Mode | None:
    """
    Gets most played bedwars modes (solos, doubles, etc).

    :param bedwars_data: The Hypixel bedwars data of the player.
    """
    # return get_most_mode(bedwars_data, 'games_played_bedwars')
    return get_most_mode_v2(bedwars_data, "games_played_bedwars", dreams)


def calc_xp_from_wins(bedwars_data: BedwarsData) -> dict[str, int]:
    """
    Calculate the total amount of xp a player has been awarded for
    winning bedwars games. Accounts for xp differences between modes.

    :param bedwars_data: The Hypixel bedwars data of the player.
    :return dict[str, int]: A dictionary of modes and their xp, as well \
        as the total xp.
    """
    exp_data = {"experience": 0}

    for mode, exp_amount in WINS_XP_MAP.items():
        total_wins = bedwars_data.get(mode, 0)

        mode_exp = total_wins * exp_amount

        exp_data[mode] = mode_exp
        exp_data["experience"] += mode_exp

    return exp_data


def rround(number: float | int, ndigits: int = 0) -> float | int:
    """
    Round a number to a specified number of decimal places. If the number is a
    whole number, it will be converted to an int.

    :param number: The number to be rounded.
    :param ndigits: The number of decimal places to round to.
    :return float | int: The rounded number.
    """
    rounded = float(round(number, ndigits))
    if rounded.is_integer():
        rounded = int(rounded)
    return rounded


def add_suffixes(*args: int) -> list[str] | str:
    """
    Add suffixes to the end of large numbers to approximate them.

    :param *args: The number(s) to approximate.
    :return list[str] | str: The approximated number(s).
    """
    formatted_values: list[str] = []
    for value in args:
        for num, suffix in NUM_SUFFIXES_MAP.items():
            if value >= num:
                fmt_value: str = f"{value/num:,.1f}{suffix}"
                break
        else:
            fmt_value: str = f"{rround(value, 2):,}"
        formatted_values.append(fmt_value)

    return formatted_values[0] if len(formatted_values) == 1 else formatted_values


def ratio(dividend: int | float, divisor: int | float) -> int | float:
    """
    Safely gets the ratio of 2 numbers nicely rounded to
    2 decimal places without dividing by 0.

    :param dividend: The dividend value in the division.
    :param divisor: The divisor value in the division.
    :return int | float: The ratio of the 2 numbers.
    """
    return rround(dividend / (divisor or 1), 2)
