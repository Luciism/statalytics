"""Account themes related functionality."""

from dataclasses import dataclass
from typing import TypeVar

from ..errors import ThemeNotFoundError
from ..cfg import config
from ..db import ensure_cursor, Cursor


def get_voter_themes() -> list[str]:
    """Return a list of available voter themes from the config file."""
    themes: dict = config('global.theme_packs.voter_themes')
    return list(themes.keys())

def get_exclusive_themes() -> list[str]:
    """Return a list of available exclusive themes from the config file."""
    themes: dict = config('global.theme_packs.exclusive_themes')
    return list(themes.keys())

def get_theme_properties(theme_name: str) -> dict:
    """
    Get the properties of a specified theme.
    Works for both voter and exclusive themes.

    :param theme_name: The name of the theme to get the properties of.
    """
    theme_packs: dict = config('global.theme_packs')

    theme_properties = theme_packs.get('voter_themes', {}).get(theme_name)

    if theme_properties is None:
        theme_properties = theme_packs.get('exclusive_themes', {}).get(theme_name)

        if theme_properties is None:
            raise ThemeNotFoundError("The specified theme does not exist!")

    return theme_properties


@dataclass
class ThemesData:
    """Represents the themes data for a user."""
    discord_id: int
    "The user's Discord ID."
    owned_themes: list[str]
    "A list of the user's owned themes."
    active_theme: str | None
    "The user's active theme."


class AccountThemes:
    """Manager for account themes."""
    def __init__(self, discord_id: int) -> None:
        self._discord_user_id = discord_id

    def _raise_if_exclusive_not_found(self, theme_name: str) -> None:
        exclusive_themes = get_exclusive_themes()
        if not theme_name in exclusive_themes:
            raise ThemeNotFoundError(
                'The respective theme is not a valid exclusive theme!')

    def _raise_if_unavailable(self, theme_name: str) -> None:
        if not theme_name in self.get_available_themes():
            raise ThemeNotFoundError(f'Theme `{theme_name}` is not an available theme!')

    @ensure_cursor
    def load(self, *, cursor: Cursor=None) -> ThemesData:
        """Load the user's themes from the database."""
        themes_data = cursor.execute(
            'SELECT * FROM themes_data WHERE discord_id = ?',
            (self._discord_user_id,)
        ).fetchone()

        if themes_data:
            return ThemesData(
                self._discord_user_id,
                [theme for theme in (themes_data[1] or '').split(',') if theme],
                themes_data[2]
            )

        return ThemesData(self._discord_user_id, [], None)

    @ensure_cursor
    def get_owned_themes(self, *, cursor: Cursor=None) -> list[str]:
        """
        Retrieve a list of themes owned by the user.

        :return list: A list of the user's owned themes.
        """
        return self.load(cursor=cursor).owned_themes

    @ensure_cursor
    def get_available_themes(self, *, cursor: Cursor=None) -> list[str]:
        """Retrieve all themes available to the user."""
        return self.get_owned_themes(cursor=cursor) + get_voter_themes()

    @ensure_cursor
    def add_owned_theme(self, theme_name: str, *, cursor: Cursor=None) -> None:
        """
        Gives the user a theme by the given name.

        :param theme_name: The name of the theme to be given to the user.
        """
        self._raise_if_exclusive_not_found(theme_name)

        themes_data = cursor.execute(
            "SELECT * FROM themes_data WHERE discord_id = ?", (self._discord_user_id,)
        ).fetchone()

        if themes_data:
            owned_str = themes_data[1]
            owned_list = owned_str.split(',') if owned_str else []

            if not theme_name in owned_list:
                owned_list.append(theme_name)
                cursor.execute(
                    "UPDATE themes_data SET owned_themes = ? WHERE discord_id = ?",
                    (','.join(owned_list), self._discord_user_id))
        else:
            cursor.execute(
                'INSERT INTO themes_data (discord_id, owned_themes) VALUES (?, ?)',
                (self._discord_user_id, theme_name)
            )

    @ensure_cursor
    def remove_owned_theme(self, theme_name: str, *, cursor: Cursor=None) -> None:
        """
        Remove an owned theme from the user's account.

        :param theme_name: The name of the theme to remove from the user.
        """
        owned_themes = cursor.execute(
            "SELECT owned_themes FROM themes_data WHERE discord_id = ?",
            (self._discord_user_id,)
        ).fetchone()

        if owned_themes and (owned_themes[0]):
            owned_themes: list = owned_themes[0].split(',')

            if theme_name in owned_themes:
                owned_themes.remove(theme_name)
                cursor.execute(
                    "UPDATE themes_data SET owned_themes = ? WHERE discord_id = ?",
                    (','.join(owned_themes) if owned_themes else None, self._discord_user_id)
                )

    @ensure_cursor
    def set_owned_themes(self, themes: list, *, cursor: Cursor=None) -> None:
        """
        Sets the user's owned themes to a list of given themes.
        This will overwrite any existing owned themes.

        :param themes: The list of themes to set for a user.
        """
        # If a single theme is given, convert it to a list
        if isinstance(themes, str):
            themes = [themes]

        # Ensure all themes are ownable
        themes = [theme for theme in themes if theme in get_exclusive_themes()]

        themes_data = cursor.execute(
            "SELECT * FROM themes_data WHERE discord_id = ?", (self._discord_user_id,)
        ).fetchone()

        if themes_data:
            cursor.execute(
                "UPDATE themes_data SET owned_themes = ? WHERE discord_id = ?",
                (','.join(themes), self._discord_user_id)
            )
        else:
            cursor.execute(
                'INSERT INTO themes_data (discord_id, owned_themes) VALUES (?, ?)',
                (self._discord_user_id, ','.join(themes))
            )

    DefaultT = TypeVar("DefaultT")

    @ensure_cursor
    def get_active_theme(
        self,
        default: DefaultT='none',
        *, cursor: Cursor=None
    ) -> str | DefaultT:
        """
        Get the user's current active theme pack.

        :param default: The default value to return if the user has no active theme.
        """
        return self.load(cursor=cursor).active_theme or default

    @ensure_cursor
    def set_active_theme(self, theme_name: str, *, cursor: Cursor=None) -> None:
        """
        Sets the user's active theme to the given theme.

        :param theme_name: The name of the theme to set as active.
        """
        self._raise_if_unavailable(theme_name)

        themes_data = cursor.execute(
            'SELECT * FROM themes_data WHERE discord_id = ?', (self._discord_user_id,)
        ).fetchone()

        if themes_data:
            cursor.execute(
                "UPDATE themes_data SET selected_theme = ? WHERE discord_id = ?",
                (theme_name, self._discord_user_id)
            )
        else:
            cursor.execute(
                "INSERT INTO themes_data (discord_id, selected_theme) VALUES (?, ?)",
                (self._discord_user_id, theme_name)
            )

    @ensure_cursor
    def delete_all_theme_data(self, *, cursor: Cursor=None) -> None:
        """
        Irreversibly delete all the user's theme data.
        """
        cursor.execute(
            'DELETE FROM themes_data WHERE discord_id = ?',
            (self._discord_user_id,))
