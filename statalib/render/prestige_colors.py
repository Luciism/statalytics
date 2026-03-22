"""Functionality for formatting prestige colors."""

from dataclasses import dataclass
from enum import Enum
import logging
from typing import final

from ..color import Color, ColorString


@final
class PrestigeColorMaps:
    """Bedwars prestige color maps."""
    c = ColorString

    prestige_map = {
        10000: c.RED,
        900: c.DARK_PURPLE,
        800: c.BLUE,
        700: c.LIGHT_PURPLE,
        600: c.DARK_RED,
        500: c.DARK_AQUA,
        400: c.DARK_GREEN,
        300: c.AQUA,
        200: c.GOLD,
        100: c.WHITE,
        0: c.GRAY,
    }
    "Prestige colors for levels 0-900 & 10000+."

    prestige_map_2 = {
        5000: (c.DARK_RED, c.DARK_RED, c.DARK_PURPLE, c.BLUE, c.BLUE, c.DARK_BLUE, c.BLACK),
        4900: (c.DARK_GREEN, c.GREEN, c.WHITE, c.WHITE, c.GREEN, c.GREEN, c.DARK_GREEN),
        4800: (c.DARK_PURPLE, c.DARK_PURPLE, c.RED, c.GOLD, c.YELLOW, c.AQUA, c.DARK_AQUA),
        4700: (c.WHITE, c.DARK_RED, c.RED, c.RED, c.BLUE, c.DARK_BLUE, c.BLUE),
        4600: (c.DARK_AQUA, c.AQUA, c.YELLOW, c.YELLOW, c.GOLD, c.LIGHT_PURPLE, c.DARK_PURPLE),
        4500: (c.WHITE, c.WHITE, c.AQUA, c.AQUA, c.DARK_AQUA, c.DARK_AQUA, c.DARK_AQUA),
        4400: (c.DARK_GREEN, c.DARK_GREEN, c.GREEN, c.YELLOW, c.GOLD, c.DARK_PURPLE, c.LIGHT_PURPLE),
        4300: (c.BLACK, c.DARK_PURPLE, c.DARK_GRAY, c.DARK_GRAY, c.DARK_PURPLE, c.DARK_PURPLE, c.BLACK),
        4200: (c.DARK_BLUE, c.BLUE, c.DARK_AQUA, c.AQUA, c.WHITE, c.GRAY, c.GRAY),
        4100: (c.YELLOW, c.YELLOW, c.GOLD, c.RED, c.LIGHT_PURPLE, c.LIGHT_PURPLE, c.DARK_PURPLE),
        4000: (c.DARK_PURPLE, c.DARK_PURPLE, c.RED, c.RED, c.GOLD, c.GOLD, c.YELLOW),
        3900: (c.RED, c.RED, c.GREEN, c.GREEN, c.DARK_AQUA, c.BLUE, c.BLUE),
        3800: (c.DARK_BLUE, c.DARK_BLUE, c.BLUE, c.DARK_PURPLE, c.DARK_PURPLE, c.LIGHT_PURPLE, c.DARK_BLUE),
        3700: (c.DARK_RED, c.DARK_RED, c.RED, c.RED, c.AQUA, c.DARK_AQUA, c.DARK_AQUA),
        3600: (c.GREEN, c.GREEN, c.GREEN, c.AQUA, c.BLUE, c.BLUE, c.DARK_BLUE),
        3500: (c.RED, c.RED, c.DARK_RED, c.DARK_RED, c.DARK_GREEN, c.GREEN, c.GREEN),
        3400: (c.DARK_GREEN, c.GREEN, c.LIGHT_PURPLE, c.LIGHT_PURPLE, c.DARK_PURPLE, c.DARK_PURPLE, c.GREEN),
        3300: (c.BLUE, c.BLUE, c.BLUE, c.LIGHT_PURPLE, c.RED, c.RED, c.DARK_RED),
        3200: (c.RED, c.DARK_RED, c.GRAY, c.GRAY, c.DARK_RED, c.RED, c.RED),
        3100: (c.BLUE, c.BLUE, c.DARK_AQUA, c.DARK_AQUA, c.GOLD, c.GOLD, c.YELLOW),
        3000: (c.YELLOW, c.YELLOW, c.GOLD, c.GOLD, c.RED, c.RED, c.DARK_RED),
        2900: (c.AQUA, c.AQUA, c.DARK_AQUA, c.DARK_AQUA, c.BLUE, c.BLUE, c.BLUE),
        2800: (c.GREEN, c.GREEN, c.DARK_GREEN, c.DARK_GREEN, c.GOLD, c.GOLD, c.YELLOW),
        2700: (c.YELLOW, c.YELLOW, c.WHITE, c.WHITE, c.DARK_GRAY, c.DARK_GRAY, c.DARK_GRAY),
        2600: (c.DARK_RED, c.DARK_RED, c.RED, c.RED, c.LIGHT_PURPLE, c.LIGHT_PURPLE, c.DARK_PURPLE),
        2500: (c.WHITE, c.WHITE, c.GREEN, c.GREEN, c.DARK_GREEN, c.DARK_GREEN, c.DARK_GREEN),
        2400: (c.AQUA, c.AQUA, c.WHITE, c.WHITE, c.GRAY, c.GRAY, c.DARK_GRAY),
        2300: (c.DARK_PURPLE, c.DARK_PURPLE, c.LIGHT_PURPLE, c.LIGHT_PURPLE, c.GOLD, c.YELLOW, c.YELLOW),
        2200: (c.GOLD, c.GOLD, c.WHITE, c.WHITE, c.AQUA, c.DARK_AQUA, c.DARK_AQUA),
        2100: (c.WHITE, c.WHITE, c.YELLOW, c.YELLOW, c.GOLD, c.GOLD, c.GOLD),
        2000: (c.DARK_GRAY, c.GRAY, c.WHITE, c.WHITE, c.GRAY, c.GRAY, c.DARK_GRAY),
        1900: (c.GRAY, c.DARK_PURPLE, c.DARK_PURPLE, c.DARK_PURPLE, c.DARK_PURPLE, c.DARK_GRAY, c.GRAY),
        1800: (c.GRAY, c.BLUE, c.BLUE, c.BLUE, c.BLUE, c.DARK_BLUE, c.GRAY),
        1700: (c.GRAY, c.LIGHT_PURPLE, c.LIGHT_PURPLE, c.LIGHT_PURPLE, c.LIGHT_PURPLE, c.DARK_PURPLE, c.GRAY),
        1600: (c.GRAY, c.RED, c.RED, c.RED, c.RED, c.DARK_RED, c.GRAY),
        1500: (c.GRAY, c.DARK_AQUA, c.DARK_AQUA, c.DARK_AQUA, c.DARK_AQUA, c.BLUE, c.GRAY),
        1400: (c.GRAY, c.GREEN, c.GREEN, c.GREEN, c.GREEN, c.DARK_GREEN, c.GRAY),
        1300: (c.GRAY, c.AQUA, c.AQUA, c.AQUA, c.AQUA, c.DARK_AQUA, c.GRAY),
        1200: (c.GRAY, c.YELLOW, c.YELLOW, c.YELLOW, c.YELLOW, c.GOLD, c.GRAY),
        1100: (c.GRAY, c.WHITE, c.WHITE, c.WHITE, c.WHITE, c.GRAY, c.GRAY),
        1000: (c.RED, c.GOLD, c.YELLOW, c.GREEN, c.AQUA, c.LIGHT_PURPLE, c.DARK_PURPLE),
    }
    "Prestige colors for levels 1000 - 9900 (unique coloring stops at level 5000)."


class PrestigeColorEnum(Enum):
    """Whether a prestige is a single color or multiple."""
    SINGLE = 0
    "A single RGB color."
    MULTI = 1
    "Multiple RGB colors."

PrestigeColorSingle = ColorString
PrestigeColorMulti = tuple[ColorString, ColorString, ColorString, ColorString, ColorString, ColorString, ColorString]

@dataclass
class PrestigeColorType:
    "A prestige color type."
    type: PrestigeColorEnum
    "Whether the prestige is a single color or multiple."
    color: PrestigeColorSingle | PrestigeColorMulti
    "The color(s) of the prestige."


class PrestigeColors:
    """Class for determining prestige colors."""
    def __init__(self, prestige: int) -> None:
        """
        Initialize the class.

        :param prestige: The prestige to determine the colors for.
        """
        self._prestige = prestige
        self.__prestige_colors = None
        self.__prestige_primary_rgb = None


    @property
    def prestige_colors(self) -> PrestigeColorType:
        """
        The prestige colors for a given prestige.
        Any prestige below 1000 (or above 10000) will be a single RGB, and anything
        from 1000 to 9900 will have an assigned color for each character in the
        formatted level.
        """
        if self.__prestige_colors is None:
            c = PrestigeColorMaps

            if 1000 <= self._prestige < 10000:
                color = c.prestige_map_2.get(self._prestige, c.prestige_map_2.get(5000))
                self.__prestige_colors = PrestigeColorType(PrestigeColorEnum.MULTI, color)
                return self.__prestige_colors

            color =  c.prestige_map.get(self._prestige, c.prestige_map.get(10000))
            self.__prestige_colors = PrestigeColorType(PrestigeColorEnum.SINGLE, color)

        return self.__prestige_colors

    @property
    def primary_prestige_color(self) -> tuple[int, int, int]:
        """The primary color of the prestige as RGB."""
        if self.__prestige_primary_rgb is None:

            prestige_colors = self.prestige_colors.color
            if type(prestige_colors) != PrestigeColorSingle:
                pres_color = prestige_colors[0]
            else:
                pres_color = prestige_colors

            self.__prestige_primary_rgb = pres_color.value.rgb
        return self.__prestige_primary_rgb

    @staticmethod
    def _single_prestige_color_gradient(color: PrestigeColorSingle):
        rgbs = [
            tuple([int(c * (1 - 0.125 * 3.5)) for c in color.value.rgb]),
            tuple([int(c * (1 - 0.125 * 3)) for c in color.value.rgb]),
            tuple([int(c * (1 - 0.125 * 2.5)) for c in color.value.rgb]),
            tuple([int(c * (1 - 0.125 * 2)) for c in color.value.rgb]),
            tuple([int(c * (1 - 0.125 * 1.5)) for c in color.value.rgb]),
            tuple([int(c * (1 - 0.125 * 1)) for c in color.value.rgb]),
            color.value.rgb
        ]

        return tuple([Color(rgb) for rgb in rgbs])

    @property
    def seven_step_gradient(self) -> tuple[Color, Color, Color, Color, Color, Color, Color]:
        if type(self.prestige_colors.color) != PrestigeColorSingle:
            return tuple([c.value for c in self.prestige_colors.color])
        
        return self._single_prestige_color_gradient(self.prestige_colors.color)

class Prestige:
    """Class for determining and formatting prestige levels."""
    bedwars_star_symbol_map = {
        3100: '✥',
        2100: '⚝',
        1100: '✪',
        0: '✫'
    }
    "Maps the prestige to their respective star symbol."

    def __init__(self, level: int) -> None:
        """
        Initialize the class.

        :param level: The level to operate on.
        """
        self._level = level
        self.colors = PrestigeColors(self.prestige)
        self.__star_symbol = None
        self.__formatted_level_str = None

    @property
    def prestige(self) -> int:
        """The rounded prestige number of the level."""
        return self._level // 100 * 100

    @property
    def star_symbol(self) -> str:
        """The star symbol respective to the prestige."""
        if self.__star_symbol is None:
            for key, value in self.bedwars_star_symbol_map.items():
                if self._level >= key:
                    self.__star_symbol = value
                    break
            else:
                self.__star_symbol = self.bedwars_star_symbol_map.get(0)

        return self.__star_symbol

    @property
    def formatted_level(self) -> str:
        """Format the level with colors, brackets, and the star symbol."""
        if self.__formatted_level_str is None:
            prestige_colors = self.colors.prestige_colors

            star_symbol = self.star_symbol
            level_string = f'[{self._level}{star_symbol}]'

            if prestige_colors.type == PrestigeColorEnum.MULTI:
                self.__formatted_level_str = ''.join([
                    f'{prestige_colors.color[i].to_color_code()}{char}' for i, char in enumerate(level_string)
                ])
            else:
                self.__formatted_level_str = f'{prestige_colors.color.to_color_code()}{level_string}'

        return self.__formatted_level_str

    def char_to_color_map(self) -> list[tuple[str, Color]]:
        level_str = f"[{self._level}{self.star_symbol}]"

        if type(self.colors.prestige_colors.color) != PrestigeColorSingle:
            return list(zip(level_str, [c.value for c in self.colors.prestige_colors.color]))

        return [(level_str, self.colors.prestige_colors.color.value)]

    @staticmethod
    def format_level(level: int) -> str:
        """Standalone method for formatting a level."""
        return Prestige(level).formatted_level
