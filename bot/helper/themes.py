import sqlite3

from .errors import ThemeNotFoundError
from .functions import get_config, REL_PATH


def get_owned_themes(discord_id: int) -> list:
    """
    Returns list of themes owned by a discord user
    :param discord_id: the discord id of the respective user
    """
    with sqlite3.connect(f'{REL_PATH}/database/voting.db') as conn:
        cursor = conn.cursor()

        cursor.execute(
            f'SELECT owned_themes FROM owned_themes WHERE discord_id = {discord_id}')
        owned_themes: tuple = cursor.fetchone()
    
    if owned_themes:
        return owned_themes[0].split(',')
    return []


def get_voter_themes() -> list:
    """
    Returns a list of voter themes
    """
    config_data = get_config()
    themes: dict = config_data['theme_packs']['voter_themes']

    return list(themes.keys())


def get_exclusive_themes() -> list:
    """
    Returns a list of exclusive themes
    """
    config_data = get_config()
    themes: dict = config_data['theme_packs']['exclusive_themes']

    return list(themes.keys())


def add_owned_theme(discord_id: int, theme_name: str):
    """
    Gives the user a theme by the given name
    :param discord_id: the discord id of the respective user
    :param theme_name: the name of the theme to be given to the user
    """
    with sqlite3.connect(f'{REL_PATH}/database/voting.db') as conn:
        cursor = conn.cursor()
        cursor.execute(
            f"SELECT owned_themes FROM owned_themes WHERE discord_id = {discord_id}")

        owned_themes = cursor.fetchone()

        if owned_themes:
            if not theme_name in owned_themes[0].split(','):
                cursor.execute(
                    f"UPDATE owned_themes SET owned_themes = ? WHERE discord_id = ?",
                    (f'{owned_themes[0]},{theme_name}', discord_id)
                )
        else:
            cursor.execute(
                f'INSERT INTO owned_themes (discord_id, owned_themes) VALUES (?, ?)',
                (discord_id, theme_name)
            )


def remove_owned_theme(discord_id: int, theme_name: str):
    """
    Removes a theme from a user with a specified discord id
    :param discord_id: the discord id of the respective user
    :param theme_name: the name of the theme to be taken from the user
    """
    with sqlite3.connect(f'{REL_PATH}/database/voting.db') as conn:
        cursor = conn.cursor()
        cursor.execute(
            f"SELECT owned_themes FROM owned_themes WHERE discord_id = {discord_id}")

        owned_themes = cursor.fetchone()

        if owned_themes:
            owned_themes: list = owned_themes[0].split(',')

            if theme_name in owned_themes:
                if len(owned_themes) > 1:
                    owned_themes.remove(theme_name)
                    cursor.execute(
                        f"UPDATE owned_themes SET owned_themes = ? WHERE discord_id = ?",
                        (','.join(owned_themes), discord_id)
                    )
                else:
                    cursor.execute(f'DELETE FROM owned_themes WHERE discord_id = {discord_id}')


def set_owned_themes(discord_id: int, themes: list | tuple):
    """
    Sets a user's owned themes to a list of given themes
    :param discord_id: the discord id of the respective user
    :param themes: a list of themes to set for a user
    """
    if not themes:
        return

    with sqlite3.connect(f'{REL_PATH}/database/voting.db') as conn:
        cursor = conn.cursor()
        cursor.execute(f"SELECT owned_themes FROM owned_themes WHERE discord_id = {discord_id}")

        owned_themes = cursor.fetchone()

        if owned_themes:
            cursor.execute(
                f"UPDATE owned_themes SET owned_themes = ? WHERE discord_id = ?",
                (','.join(themes), discord_id)
            )
        else:
            cursor.execute(
                f'INSERT INTO owned_themes (discord_id, owned_themes) VALUES (?, ?)',
                (discord_id, ','.join(themes))
            )


def get_active_theme(discord_id: int, default='none'):
    """
    Get a user's current active theme pack
    :param discord_id: the discord id of the respective user
    :param default: the default value to return if the user has no active theme
    """
    with sqlite3.connect(f'{REL_PATH}/database/voting.db') as conn:
        cursor = conn.cursor()

        cursor.execute(
            f'SELECT enabled_theme FROM rewards_data WHERE discord_id = {discord_id}')
        rewards_data = cursor.fetchone()

    if rewards_data:
        return rewards_data[0]
    return default


def set_active_theme(discord_id: int, theme_name: str):
    """
    Sets a user's active theme to the given theme
    :param discord_id: the discord id of the respective user
    :param theme_name: the name of the theme to set as active
    """
    with sqlite3.connect(f'{REL_PATH}/database/voting.db') as conn:
        cursor = conn.cursor()

        cursor.execute(
            f'SELECT enabled_theme FROM rewards_data WHERE discord_id = {discord_id}')
        rewards_data = cursor.fetchone()

        if rewards_data:
            cursor.execute(
                f"UPDATE rewards_data SET enabled_theme = ? WHERE discord_id = ?",
                (theme_name, discord_id)    
            )
        else:
            cursor.execute(
                f"INSERT INTO rewards_data (discord_id, enabled_theme) VALUES (?, ?)",
                (discord_id, theme_name)
            )


class ThemeManager:
    def __init__(self, discord_id: int):
        self.discord_id = discord_id


    def _check_exclusive_exists(self, theme_name: str):
        exclusive_themes = get_exclusive_themes()
        if not theme_name in exclusive_themes:       
            raise ThemeNotFoundError('The respective theme is not a valid exclusive theme!')


    def get_owned_themes(self):
        """
        Returns a list of owned themes
        """
        return get_owned_themes(self.discord_id)
    

    def get_available_themes(self):
        """
        Returns all themes available to a user
        """
        return get_owned_themes(self.discord_id) + get_voter_themes()


    def add_owned_theme(self, theme_name: str):
        """
        Gives the user a theme by the given name
        :param theme_name: the name of the theme to be given to the user
        """
        self._check_exclusive_exists(theme_name)
        add_owned_theme(self.discord_id, theme_name)


    def remove_owned_theme(self, theme_name: str):
        """
        Removes a theme from the user
        :param theme_name: the name of the theme to be taken from the user
        """
        self._check_exclusive_exists(theme_name)
        remove_owned_theme(self.discord_id, theme_name)


    def set_owned_themes(self, themes: list):
        """
        Sets the user's owned themes to a list of given themes
        :param themes: a list of themes to set for a user
        """
        exclusive_themes = get_exclusive_themes()
        if isinstance(themes, str):
            themes = [themes]
        set_owned_themes(
            self.discord_id,
            [theme for theme in themes if theme in exclusive_themes]
        )


    def get_active_theme(self, default=None):
        """
        Get the user's current active theme pack
        :param default: the default value to return if the user has no active theme
        """
        return get_active_theme(self.discord_id, default)


    def set_active_theme(self, theme_name: str):
        """
        Sets the user's active theme to the given theme
        :param theme_name: the name of the theme to set as active
        """
        self._check_exclusive_exists(theme_name)
        set_active_theme(self.discord_id, theme_name)
