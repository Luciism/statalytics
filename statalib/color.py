"""Minecraft color code mappings."""

from enum import Enum
from typing import final


@final
class Color:
    def __init__(self, rgb: tuple[int, int, int]) -> None:
        self._rgb = rgb

    @property
    def hex(self) -> str:
        def clamp(x: int): 
          return max(0, min(x, 255))

        r, g, b = self._rgb
        return "#{0:02x}{1:02x}{2:02x}".format(clamp(r), clamp(g), clamp(b))

    @property
    def rgb(self) -> tuple[int, int, int]:
        return self._rgb


    @staticmethod
    def from_color_code(color_code: str) -> 'Color':
        return COLOR_CODE_MAP[color_code].value

    @staticmethod
    def from_color_str(color: str) -> 'Color':
        return ColorString.from_str(color).value

class ColorString(Enum):
    BLACK = Color((0, 0, 0))
    DARK_BLUE = Color((0, 0, 170))
    DARK_GREEN = Color((0, 170, 0))
    DARK_AQUA = Color((0, 170, 170))
    DARK_RED = Color((170, 0, 0))
    DARK_PURPLE = Color((170, 0, 170))
    GOLD = Color((255, 170, 0))
    GRAY = Color((170, 170, 170))
    DARK_GRAY = Color((85, 85, 85))
    BLUE = Color((85, 85, 255))
    GREEN = Color((85, 255, 85))
    AQUA = Color((85, 255, 255))
    RED = Color((255, 85, 85))
    LIGHT_PURPLE = Color((255, 85, 255))
    YELLOW = Color((255, 255, 85))
    WHITE = Color((255, 255, 255))

    @staticmethod
    def from_str(color: str) -> 'ColorString':
        return ColorString.__getattribute__(ColorString.WHITE, color)

    def to_color_code(self) -> str:
        inverse = {v: k for k, v in COLOR_CODE_MAP.items()}
        return inverse[self]

COLOR_CODE_MAP = {
    '&0': ColorString.BLACK,
    '&1': ColorString.DARK_BLUE,
    '&2': ColorString.DARK_GREEN,
    '&3': ColorString.DARK_AQUA,
    '&4': ColorString.DARK_RED,
    '&5': ColorString.DARK_PURPLE,
    '&6': ColorString.GOLD,
    '&7': ColorString.GRAY,
    '&8': ColorString.DARK_GRAY,
    '&9': ColorString.BLUE,
    '&a': ColorString.GREEN,
    '&b': ColorString.AQUA,
    '&c': ColorString.RED,
    '&d': ColorString.LIGHT_PURPLE,
    '&e': ColorString.YELLOW,
    '&f': ColorString.WHITE,
}

STR_TO_COLOR_CODE_MAP = {
    'BLACK': '&0',
    'DARK_BLUE': '&1',
    'DARK_GREEN': '&2',
    'DARK_AQUA': '&3',
    'DARK_RED': '&4',
    'DARK_PURPLE': '&5',
    'GOLD': '&6',
    'GRAY': '&7',
    'DARK_GRAY': '&8',
    'BLUE': '&9',
    'GREEN': '&a',
    'AQUA': '&b',
    'RED': '&c',
    'LIGHT_PURPLE': '&d',
    'YELLOW': '&e',
    'WHITE': '&f',
}

@final
class ColorCode:
    def __init__(self, color_code: str) -> None:
        self._color_code = color_code

    @staticmethod
    def from_str(color: str) -> 'ColorCode':
        return ColorCode(STR_TO_COLOR_CODE_MAP[color])

    @property
    def color(self) -> Color:
        return COLOR_CODE_MAP[self._color_code].value


@final
class ColorMappings:
    """Minecraft color code mapping class."""
    black = (0, 0, 0)
    "Black RGB value."
    dark_blue = (0, 0, 170)
    "Dark blue RGB value."
    dark_green = (0, 170, 0)
    "Dark green RGB value."
    dark_aqua = (0, 170, 170)
    "Dark aqua RGB value."
    dark_red = (170, 0, 0)
    "Dark red RGB value."
    dark_purple = (170, 0, 170)
    "Dark purple RGB value."
    gold = (255, 170, 0)
    "Gold RGB value."
    gray = (170, 170, 170)
    "Gray RGB value."
    dark_gray = (85, 85, 85)
    "Dark gray RGB value."
    blue = (85, 85, 255)
    "Blue RGB value."
    green = (85, 255, 85)
    "Green RGB value."
    aqua = (85, 255, 255)
    "Aqua RGB value."
    red = (255, 85, 85)
    "Red RGB value."
    light_purple = (255, 85, 255)
    "Light purple RGB value."
    yellow = (255, 255, 85)
    "Yellow RGB value."
    white = (255, 255, 255)
    "White RGB value."

    color_codes: dict[str, tuple[int, int, int]] = {
        '&0': black,
        '&1': dark_blue,
        '&2': dark_green,
        '&3': dark_aqua,
        '&4': dark_red,
        '&5': dark_purple,
        '&6': gold,
        '&7': gray,
        '&8': dark_gray,
        '&9': blue,
        '&a': green,
        '&b': aqua,
        '&c': red,
        '&d': light_purple,
        '&e': yellow,
        '&f': white
    }
    "Color code to RGB value mapping."

    str_to_color_code = {
        'black': '&0',
        'dark_blue': '&1',
        'dark_green': '&2',
        'dark_aqua': '&3',
        'dark_red': '&4',
        'dark_purple': '&5',
        'gold': '&6',
        'gray': '&7',
        'dark_gray': '&8',
        'blue': '&9',
        'green': '&a',
        'aqua': '&b',
        'red': '&c',
        'light_purple': '&d',
        'yellow': '&e',
        'white': '&f',
    }
    "Color name to color code mapping."

