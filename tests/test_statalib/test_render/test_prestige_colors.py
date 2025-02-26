import unittest

from statalib.render import Prestige, PrestigeColors, BackgroundImageLoader, ImageRender

# TODO
class TestPrestigeColorFormatting(unittest.TestCase):
    def test_format_level_0(self):
        self.assertEqual(Prestige(0).formatted_level, "&7[0✫]")
