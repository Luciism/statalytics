class ColorMappings:
    black = (0, 0, 0)
    dark_blue = (0, 0, 170)
    dark_green = (0, 170, 0)
    dark_aqua = (0, 170, 170)
    dark_red = (170, 0, 0)
    dark_purple = (170, 0, 170)
    gold = (255, 170, 0)
    gray = (170, 170, 170)
    dark_gray = (85, 85, 85)
    blue = (85, 85, 255)
    green = (85, 255, 85)
    aqua = (85, 255, 255)
    red = (255, 85, 85)
    light_purple = (255, 85, 255)
    yellow = (255, 255, 85)
    white = (255, 255, 255)

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
