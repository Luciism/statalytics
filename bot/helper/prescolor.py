class ColorMaps:
    """
    Bedwars prestige color maps
    color_map: level 0-900 & 10000+
    color_map_2: 1000 - 9900

    """
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
    dark_blue = (0, 0, 170)
    black = (0, 0, 0)

    color_map = {
        10000: red,
        900: dark_purple,
        800: blue,
        700: light_purple,
        600: dark_red,
        500: dark_aqua,
        400: dark_green,
        300: aqua,
        200: gold,
        100: white,
        0: gray,
    }

    color_map_2 = {
        5000: (dark_red, dark_red, dark_purple, blue, blue, dark_blue, black),
        4900: (dark_green, green, white, white, green, green, dark_green),
        4800: (dark_purple, dark_purple, red, gold, yellow, aqua, dark_aqua),
        4700: (white, dark_red, red, red, blue, dark_blue, blue),
        4600: (dark_aqua, aqua, yellow, yellow, gold, light_purple, dark_purple),
        4500: (white, white, aqua, aqua, dark_aqua, dark_aqua, dark_aqua),
        4400: (dark_green, dark_green, green, yellow, gold, dark_purple, light_purple),
        4300: (black, dark_purple, dark_gray, dark_gray, dark_purple, dark_purple, black),
        4200: (dark_blue, blue, dark_aqua, aqua, white, gray, gray),
        4100: (yellow, yellow, gold, red, light_purple, light_purple, dark_purple),
        4000: (dark_purple, dark_purple, red, red, gold, gold, yellow),
        3900: (red, red, green, green, dark_aqua, blue, blue),
        3800: (dark_blue, dark_blue, blue, dark_purple, dark_purple, light_purple, dark_blue),
        3700: (dark_red, dark_red, red, red, aqua, dark_aqua, dark_aqua),
        3600: (green, green, green, aqua, blue, blue, dark_blue),
        3500: (red, red, dark_red, dark_red, dark_green, green, green),
        3400: (dark_green, green, light_purple, light_purple, dark_purple, dark_purple, green),
        3300: (blue, blue, blue, light_purple, red, red, dark_red),
        3200: (red, dark_red, gray, gray, dark_red, red, red),
        3100: (blue, blue, dark_aqua, dark_aqua, gold, gold, yellow),
        3000: (yellow, yellow, gold, gold, red, red, dark_red),
        2900: (aqua, aqua, dark_aqua, dark_aqua, blue, blue, blue),
        2800: (green, green, dark_green, dark_green, gold, gold, yellow),
        2700: (yellow, yellow, white, white, dark_gray, dark_gray, dark_gray),
        2600: (dark_red, dark_red, red, red, light_purple, light_purple, dark_purple),
        2500: (white, white, green, green, dark_green, dark_green, dark_green),
        2400: (aqua, aqua, white, white, gray, gray, dark_gray),
        2300: (dark_purple, dark_purple, light_purple, light_purple, gold, yellow, yellow),
        2200: (gold, gold, white, white, aqua, dark_aqua, dark_aqua),
        2100: (white, white, yellow, yellow, gold, gold, gold),
        2000: (dark_gray, gray, white, white, gray, gray, dark_gray),
        1900: (gray, dark_purple, dark_purple, dark_purple, dark_purple, gray, gray),
        1800: (gray, blue, blue, blue, blue, dark_blue, gray),
        1700: (gray, light_purple, light_purple, light_purple, light_purple, dark_purple, gray),
        1600: (gray, red, red, red, red, dark_red, gray),
        1500: (gray, dark_aqua, dark_aqua, dark_aqua, dark_aqua, blue, gray),
        1400: (gray, green, green, green, green, dark_green, gray),
        1300: (gray, aqua, aqua, aqua, aqua, dark_aqua, gray),
        1200: (gray, yellow, yellow, yellow, yellow, gold, gray),
        1100: (gray, white, white, white, white, gray, gray),
        1000: (red, gold, yellow, green, aqua, light_purple, dark_purple)
    }

def get_prestige_colors(level: int) -> tuple:
    """
    Returns prestige colors based on level.
    Any level below 1000 or above 10000 will be a single RGB set
    Any level between 1000 and 9900 will have 7 color position values
    :param level: the level of the desired prestige color
    """
    colors = ColorMaps
    prestige = (level // 100) * 100
    if level >= 1000 and level < 10000:
        return colors.color_map_2.get(prestige, colors.color_map_2.get(5000))
    return colors.color_map.get(prestige, colors.color_map.get(10000))
