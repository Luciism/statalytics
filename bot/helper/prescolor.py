class Prescolor:
    def __init__(self, level) -> None:
        self.level = level

        self.dark_green = (0, 170, 0)
        self.dark_aqua = (0, 170, 170)
        self.dark_red = (170, 0, 0)
        self.dark_purple = (170, 0, 170)
        self.gold = (255, 170, 0)
        self.gray = (170, 170, 170)
        self.dark_gray = (85, 85, 85)
        self.blue = (85, 85, 255)
        self.green = (85, 255, 85)
        self.aqua = (85, 255, 255)
        self.red = (255, 85, 85)
        self.light_purple = (255, 85, 255)
        self.yellow = (255, 255, 85)
        self.white = (255, 255, 255)

        self.color_map = {
            10000: (self.red, "red"),
            900: (self.dark_purple, "dark_purple"),
            800: (self.blue, "blue"),
            700: (self.light_purple, "light_purple"),
            600: (self.dark_red, "dark_red"),
            500: (self.dark_aqua, "dark_aqua"),
            400: (self.dark_green, "dark_green"),
            300: (self.aqua, "aqua"),
            200: (self.gold, "gold"),
            100: (self.white, "white"),
            0: (self.gray, "gray")
        }

        self.color_map_2 = {
            3000: (self.yellow, self.yellow, self.gold, self.gold, self.red, "red", self.dark_red),
            2900: (self.aqua, self.aqua, self.dark_aqua, self.dark_aqua, self.blue, "blue", self.blue),
            2800: (self.green, self.green, self.dark_green, self.dark_green, self.gold, "gold", self.yellow),
            2700: (self.yellow, self.yellow, self.white, self.white, self.dark_gray, "dark_gray", self.dark_gray),
            2600: (self.dark_red, self.dark_red, self.red, self.red, self.light_purple, "light_purple", self.dark_purple),
            2500: (self.white, self.white, self.green, self.green, self.dark_green, "dark_green", self.dark_green),
            2400: (self.aqua, self.aqua, self.white, self.white, self.gray, "gray", self.dark_gray),
            2300: (self.dark_purple, self.dark_purple, self.light_purple, self.light_purple, self.gold, "yellow", self.yellow),
            2200: (self.gold, self.gold, self.white, self.white, self.aqua, "dark_aqua", self.dark_aqua),
            2100: (self.white, self.white, self.yellow, self.yellow, self.gold, "gold", self.gold),
            2000: (self.dark_gray, self.gray, self.white, self.white, self.gray, "gray", self.dark_gray),
            1900: (self.gray, self.dark_purple, self.dark_purple, self.dark_purple, self.dark_purple, "dark_purple", self.gray),
            1800: (self.gray, self.blue, self.blue, self.blue, self.blue, "blue", self.gray),
            1700: (self.gray, self.light_purple, self.light_purple, self.light_purple, self.light_purple, "light_purple", self.gray),
            1600: (self.gray, self.dark_red, self.dark_red, self.dark_red, self.dark_red, "dark_red", self.gray),
            1500: (self.gray, self.dark_aqua, self.dark_aqua, self.dark_aqua, self.dark_aqua, "dark_aqua", self.gray),
            1400: (self.gray, self.dark_green, self.dark_green, self.dark_green, self.dark_green, "dark_green", self.gray),
            1300: (self.gray, self.aqua, self.aqua, self.aqua, self.aqua, "aqua", self.gray),
            1200: (self.gray, self.gold, self.gold, self.gold, self.gold, "gold", self.gray),
            1100: (self.gray, self.white, self.white, self.white, self.white, "white", self.gray),
            1000: (self.red, self.gold, self.yellow, self.green, self.aqua, "light_purple", self.dark_purple)
        }

    def get_level_color(self):
        if self.level >= 1000 and self.level < 10000:
            for key in sorted(self.color_map_2.keys(), reverse=True):
                if self.level >= key:
                    pos1, pos2, pos3, pos4, pos5, pos6, pos7 = self.color_map_2[key]
                    break

            return (pos1, pos2, pos3, pos4, pos5, pos6, pos7)

        for key in sorted(self.color_map.keys(), reverse=True):
            if self.level >= key:
                pos1, pos2 = self.color_map[key]
                break
        return (pos1, None, None, None, None, pos2, None)
