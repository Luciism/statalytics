from dataclasses import dataclass
from enum import Enum

from ..color import ColorMappings


class PrestigeColorMaps:
    """
    Bedwars prestige color maps
    prestige_map: level 0-900 & 10000+
    prestige_map_2: 1000 - 9900

    """
    c = ColorMappings.str_to_color_code

    prestige_map = {
        10000: c['red'],
        900: c['dark_purple'],
        800: c['blue'],
        700: c['light_purple'],
        600: c['dark_red'],
        500: c['dark_aqua'],
        400: c['dark_green'],
        300: c['aqua'],
        200: c['gold'],
        100: c['white'],
        0: c['gray'],
    }

    prestige_map_2 = {
        5000: (c['dark_red'], c['dark_red'], c['dark_purple'], c['blue'], c['blue'], c['dark_blue'], c['black']),
        4900: (c['dark_green'], c['green'], c['white'], c['white'], c['green'], c['green'], c['dark_green']),
        4800: (c['dark_purple'], c['dark_purple'], c['red'], c['gold'], c['yellow'], c['aqua'], c['dark_aqua']),
        4700: (c['white'], c['dark_red'], c['red'], c['red'], c['blue'], c['dark_blue'], c['blue']),
        4600: (c['dark_aqua'], c['aqua'], c['yellow'], c['yellow'], c['gold'], c['light_purple'], c['dark_purple']),
        4500: (c['white'], c['white'], c['aqua'], c['aqua'], c['dark_aqua'], c['dark_aqua'], c['dark_aqua']),
        4400: (c['dark_green'], c['dark_green'], c['green'], c['yellow'], c['gold'], c['dark_purple'], c['light_purple']),
        4300: (c['black'], c['dark_purple'], c['dark_gray'], c['dark_gray'], c['dark_purple'], c['dark_purple'], c['black']),
        4200: (c['dark_blue'], c['blue'], c['dark_aqua'], c['aqua'], c['white'], c['gray'], c['gray']),
        4100: (c['yellow'], c['yellow'], c['gold'], c['red'], c['light_purple'], c['light_purple'], c['dark_purple']),
        4000: (c['dark_purple'], c['dark_purple'], c['red'], c['red'], c['gold'], c['gold'], c['yellow']),
        3900: (c['red'], c['red'], c['green'], c['green'], c['dark_aqua'], c['blue'], c['blue']),
        3800: (c['dark_blue'], c['dark_blue'], c['blue'], c['dark_purple'], c['dark_purple'], c['light_purple'], c['dark_blue']),
        3700: (c['dark_red'], c['dark_red'], c['red'], c['red'], c['aqua'], c['dark_aqua'], c['dark_aqua']),
        3600: (c['green'], c['green'], c['green'], c['aqua'], c['blue'], c['blue'], c['dark_blue']),
        3500: (c['red'], c['red'], c['dark_red'], c['dark_red'], c['dark_green'], c['green'], c['green']),
        3400: (c['dark_green'], c['green'], c['light_purple'], c['light_purple'], c['dark_purple'], c['dark_purple'], c['green']),
        3300: (c['blue'], c['blue'], c['blue'], c['light_purple'], c['red'], c['red'], c['dark_red']),
        3200: (c['red'], c['dark_red'], c['gray'], c['gray'], c['dark_red'], c['red'], c['red']),
        3100: (c['blue'], c['blue'], c['dark_aqua'], c['dark_aqua'], c['gold'], c['gold'], c['yellow']),
        3000: (c['yellow'], c['yellow'], c['gold'], c['gold'], c['red'], c['red'], c['dark_red']),
        2900: (c['aqua'], c['aqua'], c['dark_aqua'], c['dark_aqua'], c['blue'], c['blue'], c['blue']),
        2800: (c['green'], c['green'], c['dark_green'], c['dark_green'], c['gold'], c['gold'], c['yellow']),
        2700: (c['yellow'], c['yellow'], c['white'], c['white'], c['dark_gray'], c['dark_gray'], c['dark_gray']),
        2600: (c['dark_red'], c['dark_red'], c['red'], c['red'], c['light_purple'], c['light_purple'], c['dark_purple']),
        2500: (c['white'], c['white'], c['green'], c['green'], c['dark_green'], c['dark_green'], c['dark_green']),
        2400: (c['aqua'], c['aqua'], c['white'], c['white'], c['gray'], c['gray'], c['dark_gray']),
        2300: (c['dark_purple'], c['dark_purple'], c['light_purple'], c['light_purple'], c['gold'], c['yellow'], c['yellow']),
        2200: (c['gold'], c['gold'], c['white'], c['white'], c['aqua'], c['dark_aqua'], c['dark_aqua']),
        2100: (c['white'], c['white'], c['yellow'], c['yellow'], c['gold'], c['gold'], c['gold']),
        2000: (c['dark_gray'], c['gray'], c['white'], c['white'], c['gray'], c['gray'], c['dark_gray']),
        1900: (c['gray'], c['dark_purple'], c['dark_purple'], c['dark_purple'], c['dark_purple'], c['dark_gray'], c['gray']),
        1800: (c['gray'], c['blue'], c['blue'], c['blue'], c['blue'], c['dark_blue'], c['gray']),
        1700: (c['gray'], c['light_purple'], c['light_purple'], c['light_purple'], c['light_purple'], c['dark_purple'], c['gray']),
        1600: (c['gray'], c['red'], c['red'], c['red'], c['red'], c['dark_red'], c['gray']),
        1500: (c['gray'], c['dark_aqua'], c['dark_aqua'], c['dark_aqua'], c['dark_aqua'], c['blue'], c['gray']),
        1400: (c['gray'], c['green'], c['green'], c['green'], c['green'], c['dark_green'], c['gray']),
        1300: (c['gray'], c['aqua'], c['aqua'], c['aqua'], c['aqua'], c['dark_aqua'], c['gray']),
        1200: (c['gray'], c['yellow'], c['yellow'], c['yellow'], c['yellow'], c['gold'], c['gray']),
        1100: (c['gray'], c['white'], c['white'], c['white'], c['white'], c['gray'], c['gray']),
        1000: (c['red'], c['gold'], c['yellow'], c['green'], c['aqua'], c['light_purple'], c['dark_purple']),
    }

bedwars_star_symbol_map = {
    3100: '✥',
    2100: '⚝',
    1100: '✪',
    0: '✫'
}

class PrestigeColorEnum(Enum):
    single = 0
    multi = 1

@dataclass
class PrestigeColorType:
    type: PrestigeColorEnum
    color: tuple[int, int, int] | tuple[tuple[int, int, int]]

class PrestigeColors:
    def __init__(self, prestige: int) -> None:
        self._prestige = prestige
        self.__prestige_colors = None
        self.__prestige_primary_rgb = None


    @property
    def prestige_colors(self) -> PrestigeColorType:
        """
        The prestige colors for a given prestige.
        Any prestige below 1000 (or above 10000) will be a single RGB and anything
        from 1000 to 9900 will assign a color to each character in the formatted level.
        """
        if self.__prestige_colors is None:
            c = PrestigeColorMaps

            if 1000 <= self._prestige < 10000:
                color = c.prestige_map_2.get(self._prestige, c.prestige_map_2.get(5000))
                self.__prestige_colors = PrestigeColorType(PrestigeColorEnum.multi, color)
                return self.__prestige_colors

            color =  c.prestige_map.get(self._prestige, c.prestige_map.get(10000))
            self.__prestige_colors = PrestigeColorType(PrestigeColorEnum.single, color)

        return self.__prestige_colors

    @property
    def primary_prestige_color(self) -> tuple[int, int, int]:
        """The primary color of the prestige as RGB."""
        if self.__prestige_primary_rgb is None:
            pres_color_code = self.prestige_colors.color

            if self.prestige_colors.type == PrestigeColorEnum.multi:
                pres_color_code = pres_color_code[0]

            self.__prestige_primary_rgb = ColorMappings.color_codes.get(pres_color_code)
        return self.__prestige_primary_rgb


class Prestige:
    bedwars_star_symbol_map = {
        3100: '✥',
        2100: '⚝',
        1100: '✪',
        0: '✫'
    }

    def __init__(self, level: int) -> None:
        self._level = level
        self.colors = PrestigeColors(self.prestige)
        self.__star_symbol = None
        self.__formatted_level_str = None

    @property
    def prestige(self) -> int:
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
        """Formats the level with colors, brackets, and the star symbol."""
        if self.__formatted_level_str is None:
            prestige_colors = self.colors.prestige_colors

            star_symbol = self.star_symbol
            level_string = f'[{self._level}{star_symbol}]'

            if prestige_colors.type == PrestigeColorEnum.multi:
                self.__formatted_level_str = ''.join([
                    f'{prestige_colors.color[i]}{char}' for i, char in enumerate(level_string)
                ])
            else:
                self.__formatted_level_str = f'{prestige_colors.color}{level_string}'

        return self.__formatted_level_str

    @staticmethod
    def format_level(level: int) -> str:
        return Prestige(level).formatted_level
