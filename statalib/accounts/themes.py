"""Account themes related functionality."""

from typing import TypeVar
from ..errors import ThemeNotFoundError
from ..cfg import config
from ..functions import db_connect


def get_voter_themes() -> list:
    """Return a list of available voter themes from the config file."""
    themes: dict = config('global.theme_packs.voter_themes')
    return list(themes.keys())

def get_exclusive_themes() -> list:
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
        theme_properties = theme_packs.get(
            'exclusive_themes', {}).get(theme_name, {})

    return theme_properties


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
            raise ThemeNotFoundError('The respective theme is not an available theme!')

    def get_owned_themes(self) -> list[str]:
        """
        Retrieve a list of themes owned by the user.

        :return list: A list of the user's owned themes.
        """
        with db_connect() as conn:
            cursor = conn.cursor()

            cursor.execute(
                'SELECT owned_themes FROM themes_data WHERE discord_id = ?',
                (self._discord_user_id,))
            owned_themes: tuple = cursor.fetchone()

        if owned_themes and owned_themes[0]:
            return owned_themes[0].split(',')
        return []

    def get_available_themes(self) -> list[str]:
        """Retrieve all themes available to the user."""
        return self.get_owned_themes() + get_voter_themes()

    def add_owned_theme(self, theme_name: str) -> None:
        """
        Gives the user a theme by the given name.

        :param theme_name: The name of the theme to be given to the user.
        """
        self._raise_if_exclusive_not_found(theme_name)

        with db_connect() as conn:
            cursor = conn.cursor()
            cursor.execute(
                f"SELECT * FROM themes_data WHERE discord_id = ?", (self._discord_user_id,))

            themes_data = cursor.fetchone()

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

    def remove_owned_theme(self, theme_name: str) -> None:
        """
        Remove an owned theme from the user's account.

        :param theme_name: The name of the theme to remove from the user.
        """
        self._raise_if_exclusive_not_found(theme_name)

        with db_connect() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT owned_themes FROM themes_data WHERE discord_id = ?",
                (self._discord_user_id,))

            owned_themes = cursor.fetchone()

            if owned_themes and (owned_str := owned_themes[0]):
                owned_themes: list = owned_str.split(',')

                if theme_name in owned_themes:
                    owned_themes.remove(theme_name)
                    cursor.execute(
                        "UPDATE themes_data SET owned_themes = ? WHERE discord_id = ?",
                        (','.join(owned_themes) if owned_themes else None, self._discord_user_id)
                    )

    def set_owned_themes(self, themes: list) -> None:
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

        with db_connect() as conn:
            cursor = conn.cursor()
            cursor.execute(
                f"SELECT * FROM themes_data WHERE discord_id = ?", (self._discord_user_id,))

            themes_data = cursor.fetchone()

            if themes_data:
                cursor.execute(
                    "UPDATE themes_data SET owned_themes = ? WHERE discord_id = ?",
                    (','.join(themes), self._discord_user_id)
                )
            else:
                cursor.execute(
                    'INSERT INTO owned_themes (discord_id, owned_themes) VALUES (?, ?)',
                    (self._discord_user_id, ','.join(themes))
                )

    DefaultT = TypeVar("DefaultT")

    def get_active_theme(self, default: DefaultT='none') -> str | DefaultT:
        """
        Get the user's current active theme pack.

        :param default: The default value to return if the user has no active theme.
        """
        with db_connect() as conn:
            cursor = conn.cursor()

            cursor.execute(
                f'SELECT selected_theme FROM themes_data WHERE discord_id = ?',
                (self._discord_user_id,))
            selected = cursor.fetchone()

        if selected and (active := selected[0]):
            return active
        return default

    def set_active_theme(self, theme_name: str) -> None:
        """
        Sets the user's active theme to the given theme.

        :param theme_name: The name of the theme to set as active.
        """
        self._raise_if_unavailable(theme_name)

        with db_connect() as conn:
            cursor = conn.cursor()

            cursor.execute(
                f'SELECT * FROM themes_data WHERE discord_id = ?', (self._discord_user_id,))
            themes_data = cursor.fetchone()

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
