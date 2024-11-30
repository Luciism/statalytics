"""Minecraft color code mappings."""

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

    rgb_to_color_code: dict[tuple[int, int, int], str] = {
        black: '&0',
        dark_blue: '&1',
        dark_green: '&2',
        dark_aqua: '&3',
        dark_red: '&4',
        dark_purple: '&5',
        gold: '&6',
        gray: '&7',
        dark_gray: '&8',
        blue: '&9',
        green: '&a',
        aqua: '&b',
        red: '&c',
        light_purple: '&d',
        yellow: '&e',
        white: '&f'
    }
    "RGB value to color code mapping."
