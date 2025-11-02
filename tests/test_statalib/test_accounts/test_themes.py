from typing_extensions import override
import unittest

from statalib import config
from statalib.accounts import AccountThemes, themes
from statalib.accounts.themes import get_theme_by_id
from statalib.errors import ThemeNotFoundError
from tests.utils import MockData, clean_database


def setup_config():
    config._load_config_data()
    theme_packs = config._config_data.setdefault("global", {}).setdefault(
        "theme_packs", {}
    )
    voter_themes = theme_packs.setdefault("voter_themes", {})
    exclusive_themes = theme_packs.setdefault("exclusive_themes", {})

    voter_themes["test_voter"] = {"display_name": "Test Voter", "dynamic_color": False}
    voter_themes["test_voter_2"] = {
        "display_name": "Test Voter 2",
        "dynamic_color": False,
    }

    exclusive_themes["test_exclusive"] = {
        "display_name": "Test Exclusive",
        "dynamic_color": False,
    }
    exclusive_themes["test_exclusive_2"] = {
        "display_name": "Test Exclusive 2",
        "dynamic_color": False,
    }


class TestCaseBase(unittest.TestCase):
    @classmethod
    @override
    def setUpClass(cls) -> None:
        setup_config()

    @classmethod
    @override
    def tearDownClass(cls) -> None:
        config.refresh()

    @override
    def setUp(self) -> None:
        clean_database()


class TestAddOwnedTheme(TestCaseBase):
    def test_add_owned_theme(self):
        t = AccountThemes(MockData.discord_id)
        t.add_owned_theme("test_exclusive")

        self.assertIn(get_theme_by_id("test_exclusive"), t.get_owned_themes())

    def test_add_duplicate_theme(self):
        t = AccountThemes(MockData.discord_id)
        t.add_owned_theme("test_exclusive")
        t.add_owned_theme("test_exclusive")

        self.assertIn(get_theme_by_id("test_exclusive"), t.get_owned_themes())
        self.assertEqual(len(t.get_owned_themes()), 1)

    def test_add_voter_theme(self):
        t = AccountThemes(MockData.discord_id)

        with self.assertRaises(ThemeNotFoundError):
            t.add_owned_theme("test_voter")

    def test_add_unavailable_theme(self):
        t = AccountThemes(MockData.discord_id)

        with self.assertRaises(ThemeNotFoundError):
            t.add_owned_theme("test_unavailable")


class TestSetOwnedThemes(TestCaseBase):
    def test_set_owned_themes(self):
        t = AccountThemes(MockData.discord_id)
        t.set_owned_themes(["test_exclusive", "test_exclusive_2"])

        self.assertEqual(
            t.get_owned_themes(),
            [get_theme_by_id("test_exclusive"), get_theme_by_id("test_exclusive_2")],
        )

    def test_set_owned_themes_empty(self):
        t = AccountThemes(MockData.discord_id)
        t.set_owned_themes([])

        self.assertEqual(t.get_owned_themes(), [])

    def test_set_unavailable_theme(self):
        t = AccountThemes(MockData.discord_id)
        t.set_owned_themes(["test_exclusive", "test_unavailable"])

        # Skips over unavailable themes
        self.assertListEqual(t.get_owned_themes(), [get_theme_by_id("test_exclusive")])

    def set_duplicate_theme(self):
        t = AccountThemes(MockData.discord_id)
        t.set_owned_themes(["test_exclusive", "test_exclusive"])

        self.assertListEqual(t.get_owned_themes(), [get_theme_by_id("test_exclusive")])


class TestGetOwnedThemes(TestCaseBase):
    def test_get_owned_themes(self):
        t = AccountThemes(MockData.discord_id)
        t.add_owned_theme("test_exclusive")
        t.add_owned_theme("test_exclusive_2")

        self.assertEqual(
            t.get_owned_themes(),
            [get_theme_by_id("test_exclusive"), get_theme_by_id("test_exclusive_2")],
        )

    def test_get_empty_owned_themes(self):
        t = AccountThemes(MockData.discord_id)

        self.assertEqual(t.get_owned_themes(), [])


class TestRemoveOwnedTheme(TestCaseBase):
    def test_remove_owned_theme(self):
        t = AccountThemes(MockData.discord_id)
        t.add_owned_theme("test_exclusive")
        t.remove_owned_theme("test_exclusive")

        self.assertNotIn(get_theme_by_id("test_exclusive"), t.get_owned_themes())
        self.assertEqual(len(t.get_owned_themes()), 0)

    def test_remove_unowned_theme(self):
        t = AccountThemes(MockData.discord_id)
        t.add_owned_theme("test_exclusive")
        t.remove_owned_theme("test_unavailable")

        self.assertListEqual(
            t.get_owned_themes(), [themes.get_theme_by_id("test_exclusive")]
        )


class TestSetAndGetActiveTheme(TestCaseBase):
    def test_set_and_get_active_voter_theme(self):
        t = AccountThemes(MockData.discord_id)
        t.set_active_theme("test_voter")

        self.assertEqual(t.get_active_theme(), get_theme_by_id("test_voter"))

    def test_set_and_get_active_exclusive_theme(self):
        t = AccountThemes(MockData.discord_id)
        t.add_owned_theme("test_exclusive")
        t.set_active_theme("test_exclusive")

        self.assertEqual(t.get_active_theme(), get_theme_by_id("test_exclusive"))

    def test_set_and_get_active_unowned_exclusive_theme(self):
        t = AccountThemes(MockData.discord_id)

        with self.assertRaises(ThemeNotFoundError):
            t.set_active_theme("test_exclusive")

    def test_set_and_get_active_unavailable_theme(self):
        t = AccountThemes(MockData.discord_id)

        with self.assertRaises(ThemeNotFoundError):
            t.set_active_theme("test_unavailable")

    def test_get_active_theme_empty(self):
        t = AccountThemes(MockData.discord_id)

        self.assertIsNone(t.get_active_theme(default=None))
