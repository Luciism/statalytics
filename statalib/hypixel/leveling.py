"""Bedwars leveling related functionality."""

from typing import NamedTuple


def decimal_of(number: float) -> int:
    """
    Returns the decimal on the right side of the . for a floating point number,
    for example `1.521` would return `521`.

    :param number: The floating point number to find the decimal of.
    :return int: The decimal on the right side of the `.` as an integer.
    """
    return int(str(number).rsplit(maxsplit=1)[-1])


class LevelProgressionTuple(NamedTuple):
    """Leveling progression tuple."""
    progress: int
    """The xp progress made towards completing the current level."""
    target: int
    """The relative xp needed to complete the current level."""
    progress_percent: float
    """The xp progress as a percentage made towards completing the current level."""


class Leveling:
    """Leveling calculation class."""
    def __init__(
        self,
        xp: int | None=None,  # pylint: disable=invalid-name
        level: int | None=None
    ) -> None:
        """
        Initialize the class.

        *__Either__ `xp` or `level` must be provided, but not both.*

        :param xp: The xp to calculate the level from.
        :param level: The level to calculate the xp from.
        """
        assert (xp, level).count(None) == 1, "Either level or xp must be provided."

        self.__xp = xp
        self.__level = level
        self.__progression = None

    @staticmethod
    def __calc_level(xp: int) -> float:  # pylint: disable=invalid-name
        level: int = 100 * (xp // 487000)  # prestige
        xp %= 487000  # exp this prestige
        xp_map = (0, 500, 1500, 3500, 7000)

        for index, value in enumerate(xp_map):
            if xp < value:
                factor = xp_map[index-1]
                return level + ((xp - factor) / (value - factor)) + (index - 1)
        return level + (xp - 7000) / 5000 + 4

    @property
    def level(self) -> float:
        """The level as a float."""
        if self.__level is None:
            self.__level = self.__calc_level(self.xp)
        return self.__level

    @property
    def level_int(self) -> int:
        """The level as an integer."""
        return int(self.level)

    @staticmethod
    def __calc_xp(level: float):
        prestige, level = divmod(level, 100)
        xp = prestige * 487000  # pylint: disable=invalid-name
        xp_map = (0, 500, 1500, 3500, 7000)

        if level < 4:
            index = int(level)
            factor = xp_map[index]
            return int(xp + factor + (level - index) * (xp_map[index + 1] - factor))

        return int(xp + 7000 + (level - 4) * 5000)

    @property
    def xp(self) -> int:  # pylint: disable=invalid-name
        """The total amount of leveling xp."""
        if self.__xp is None:
            self.__xp = self.__calc_xp(self.level)
        return self.__xp

    @staticmethod
    def __calc_progression(level: float) -> LevelProgressionTuple:
        # levels gained this prestige
        lvls_since_pres = level % 100

        # target xp for getting to next level based on levels gained
        # this current prestige. for `0` it would be `500` xp for the next level
        # `1` would be `1000` xp, etc, otherwise if it is above `3`, it will always
        # be `5000` xp
        level_xp_map: dict = {0: 500, 1: 1000, 2: 2000, 3: 3500}
        lvl_target_xp: int = level_xp_map.get(int(lvls_since_pres), 5000)

        # Use `decimal_of()` to prevent rounding errors.
        lvl_progress_xp = float(f'.{decimal_of(level)}') * lvl_target_xp
        lvl_progress_percentage = lvl_progress_xp / lvl_target_xp * 100

        return LevelProgressionTuple(
            int(lvl_progress_xp), int(lvl_target_xp), lvl_progress_percentage)

    @property
    def progression(self) -> LevelProgressionTuple:
        """The level progress xp, the level target xp,
        and the level progress percentage."""
        if self.__progression is None:
            self.__progression = self.__calc_progression(self.level)
        return self.__progression
