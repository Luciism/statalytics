"""Account themes related functionality."""

from dataclasses import dataclass
from typing import Any, TypeVar

from typing_extensions import deprecated

from ..cfg import config
from ..db import Cursor, ensure_cursor
from ..errors import ThemeNotFoundError


@dataclass
class Theme:
    """Respresents a theme."""

    id: str
    "The unique ID of the theme."
    name: str
    "The display name of the theme."
    dynamic_color: bool
    "Whether the theme supports dynamic coloring."


DEFAULT_THEME = Theme(id="none", name="None", dynamic_color=False)


def get_theme_by_id(theme_id: str) -> Theme:
    """
    Load a the `Theme` from a theme's ID.
    :param theme_id: The ID of the theme to load.
    :raises ThemeNotFoundError: The theme ID specified does not exist.
    """
    theme_packs: dict[str, dict[str, Any]] = config("global.theme_packs")

    theme = theme_packs.get("voter_themes", {}).get(theme_id)

    if theme is None:
        theme = theme_packs.get("exclusive_themes", {}).get(theme_id)

        if theme is None:
            raise ThemeNotFoundError("The specified theme does not exist!")

    return Theme(theme_id, theme["display_name"], theme["dynamic_color"])


def get_voter_themes() -> list[Theme]:
    """Return a list of available voter themes from the config file."""
    themes: dict[str, dict[str, Any]] = config("global.theme_packs.voter_themes")

    return [
        Theme(theme_id, props["display_name"], props["dynamic_color"])
        for theme_id, props in themes.items()
    ]


def get_exclusive_themes() -> list[Theme]:
    """Return a list of available exclusive themes from the config file."""
    themes: dict[str, dict[str, Any]] = config("global.theme_packs.exclusive_themes")

    return [
        Theme(theme_id, props["display_name"], props["dynamic_color"])
        for theme_id, props in themes.items()
    ]


def get_exclusive_theme_ids() -> list[str]:
    return [theme.id for theme in get_exclusive_themes()]


# TODO: remove
@deprecated("Use get_theme_by_id() instead")
def get_theme_properties(theme_name: str) -> dict[str, Any]:
    """
    Get the properties of a specified theme.
    Works for both voter and exclusive themes.

    :param theme_name: The name of the theme to get the properties of.
    """
    theme_packs: dict = config("global.theme_packs")

    theme_properties = theme_packs.get("voter_themes", {}).get(theme_name)

    if theme_properties is None:
        theme_properties = theme_packs.get("exclusive_themes", {}).get(theme_name)

        if theme_properties is None:
            raise ThemeNotFoundError("The specified theme does not exist!")

    return theme_properties


@dataclass
class ThemesData:
    """Represents the themes data for a user."""

    discord_id: int
    "The user's Discord ID."
    owned_themes: list[Theme]
    "A list of the user's owned themes."
    active_theme: Theme | None
    "The user's active theme."


class AccountThemes:
    """Manager for account themes."""

    def __init__(self, discord_id: int) -> None:
        self._discord_user_id = discord_id

    def _raise_if_exclusive_not_found(self, theme_id: str) -> None:
        exclusive_themes = get_exclusive_themes()
        if not theme_id in [t.id for t in exclusive_themes]:
            raise ThemeNotFoundError(
                "The respective theme is not a valid exclusive theme!"
            )

    def _raise_if_unavailable(self, theme_id: str) -> None:
        if not get_theme_by_id(theme_id) in self.get_available_themes():
            raise ThemeNotFoundError(f"Theme `{theme_id}` is not an available theme!")

    @ensure_cursor
    def load(self, *, cursor: Cursor = None) -> ThemesData:
        """Load the user's themes from the database."""
        themes_data: tuple[int, str | None, str | None] | None = cursor.execute(
            "SELECT * FROM themes_data WHERE discord_id = ?", (self._discord_user_id,)
        ).fetchone()

        if themes_data:
            return ThemesData(
                self._discord_user_id,
                [
                    get_theme_by_id(theme)
                    for theme in (themes_data[1] or "").split(",")
                    if theme
                ],
                get_theme_by_id(themes_data[2]) if themes_data[2] else None,
            )

        return ThemesData(self._discord_user_id, [], None)

    @ensure_cursor
    def get_owned_themes(self, *, cursor: Cursor = None) -> list[Theme]:
        """
        Retrieve a list of themes owned by the user.

        :return list: A list of the user's owned themes.
        """
        return self.load(cursor=cursor).owned_themes

    @ensure_cursor
    def get_available_themes(self, *, cursor: Cursor = None) -> list[Theme]:
        """Retrieve all themes available to the user."""
        return self.get_owned_themes(cursor=cursor) + get_voter_themes()

    @ensure_cursor
    def add_owned_theme(self, theme_id: str, *, cursor: Cursor = None) -> None:
        """
        Gives the user a theme by the given name.

        :param theme_name: The name of the theme to be given to the user.
        """
        self._raise_if_exclusive_not_found(theme_id)

        themes_data: tuple[int, str | None, str | None] | None = cursor.execute(
            "SELECT * FROM themes_data WHERE discord_id = ?", (self._discord_user_id,)
        ).fetchone()

        if themes_data:
            owned_str = themes_data[1]
            owned_list = owned_str.split(",") if owned_str else []

            if not theme_id in owned_list:
                owned_list.append(theme_id)
                _ = cursor.execute(
                    "UPDATE themes_data SET owned_themes = ? WHERE discord_id = ?",
                    (",".join(owned_list), self._discord_user_id),
                )
        else:
            _ = cursor.execute(
                "INSERT INTO themes_data (discord_id, owned_themes) VALUES (?, ?)",
                (self._discord_user_id, theme_id),
            )

    @ensure_cursor
    def remove_owned_theme(self, theme_id: str, *, cursor: Cursor = None) -> None:
        """
        Remove an owned theme from the user's account.

        :param theme_name: The name of the theme to remove from the user.
        """
        owned_themes: tuple[str] | None = cursor.execute(
            "SELECT owned_themes FROM themes_data WHERE discord_id = ?",
            (self._discord_user_id,),
        ).fetchone()

        if owned_themes and (owned_themes[0]):
            owned_themes: list[str] = owned_themes[0].split(",")

            if theme_id in owned_themes:
                owned_themes.remove(theme_id)
                _ = cursor.execute(
                    "UPDATE themes_data SET owned_themes = ? WHERE discord_id = ?",
                    (
                        ",".join(owned_themes) if owned_themes else None,
                        self._discord_user_id,
                    ),
                )

    @ensure_cursor
    def set_owned_themes(
        self,
        themes: list[str | Theme] | list[str] | list[Theme],
        *,
        cursor: Cursor = None,
    ) -> None:
        """
        Sets the user's owned themes to a list of given themes.
        This will overwrite any existing owned themes.

        :param themes: The list of themes to set for a user.
        """
        theme_ids: list[str] = [
            theme.id if isinstance(theme, Theme) else theme for theme in themes
        ]

        # Ensure all themes are ownable
        theme_ids = [theme for theme in theme_ids if theme in get_exclusive_theme_ids()]

        themes_data = cursor.execute(
            "SELECT * FROM themes_data WHERE discord_id = ?", (self._discord_user_id,)
        ).fetchone()

        if themes_data:
            _ = cursor.execute(
                "UPDATE themes_data SET owned_themes = ? WHERE discord_id = ?",
                (",".join(theme_ids), self._discord_user_id),
            )
        else:
            _ = cursor.execute(
                "INSERT INTO themes_data (discord_id, owned_themes) VALUES (?, ?)",
                (self._discord_user_id, ",".join(theme_ids)),
            )

    DefaultT = TypeVar("DefaultT")

    @ensure_cursor
    def get_active_theme(
        self, default: DefaultT = DEFAULT_THEME, *, cursor: Cursor = None
    ) -> Theme | DefaultT:
        """
        Get the user's current active theme pack.

        :param default: The default value to return if the user has no active theme.
        """
        return self.load(cursor=cursor).active_theme or default

    @ensure_cursor
    def set_active_theme(self, theme_id: str, *, cursor: Cursor = None) -> None:
        """
        Sets the user's active theme to the given theme.

        :param theme_name: The name of the theme to set as active.
        """
        self._raise_if_unavailable(theme_id)

        themes_data = cursor.execute(
            "SELECT * FROM themes_data WHERE discord_id = ?", (self._discord_user_id,)
        ).fetchone()

        if themes_data:
            _ = cursor.execute(
                "UPDATE themes_data SET selected_theme = ? WHERE discord_id = ?",
                (theme_id, self._discord_user_id),
            )
        else:
            _ = cursor.execute(
                "INSERT INTO themes_data (discord_id, selected_theme) VALUES (?, ?)",
                (self._discord_user_id, theme_id),
            )

    @ensure_cursor
    def delete_all_theme_data(self, *, cursor: Cursor = None) -> None:
        """
        Irreversibly delete all the user's theme data.
        """
        _ = cursor.execute(
            "DELETE FROM themes_data WHERE discord_id = ?", (self._discord_user_id,)
        )
