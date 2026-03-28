"""Background loading and related functionality."""

import os
from datetime import datetime, UTC

from ..accounts import Account, themes, voting, linking
from ..common import REL_PATH
from ..errors import ThemeNotFoundError
from ..cfg import config

BG_DIR = f"{REL_PATH}/database/fractyl-custom-backgrounds"
THEME_DIR = f"{REL_PATH}/assets/fractyl-themes"


def load_custom_background(discord_user_id: int, render_name: str) -> bytes | None:
    """
    Load a custom background for a user if they have the appropriate permissions.

    If a background is not found for the specified render name, the default background
    configured by the use will be loaded (if it exists).

    :param discord_user_id: The Discord ID of the user.
    :param render_name: The name of the render to load the background for.
    """
    account = Account(discord_user_id)

    if not account.permissions.has_access("custom_backgrounds"):
        return None

    specific_img = f"{BG_DIR}/{discord_user_id}/{render_name}.png"

    if os.path.exists(specific_img):
        with open(specific_img, "rb") as img_file:
            return img_file.read()

    default_img = f"{BG_DIR}/{discord_user_id}/default.png"

    if os.path.exists(default_img):
        with open(default_img, "rb") as img_file:
            return img_file.read()

    return None


def load_theme_img(theme_id: str) -> bytes:
    """Load a theme image by its ID."""
    theme_fp = f"{THEME_DIR}/{theme_id}.png"

    if not os.path.exists(theme_fp):
        raise ThemeNotFoundError(f"No such theme at '{theme_fp}'")

    with open(theme_fp, "rb") as img_file:
        return img_file.read()


def user_has_voter_perks(voting_data: voting.VotingData) -> bool:
    """Check if a user has access to voter perks based on their voting history."""
    timestamp_now = datetime.now(UTC).timestamp()
    voter_rewards_duration: int = config('global.voting.reward_duration_hours')

    hours_since_voted = (timestamp_now - (voting_data.last_vote or 0)) / 3600
    return hours_since_voted < voter_rewards_duration


def load_user_theme(discord_user_id: int) -> bytes | None:
    """
    Load the theme image for a user if they have access to it.

    :param discord_user_id: The Discord ID of the user.
    """
    account = Account(discord_user_id)
    voter_themes_available = themes.get_voter_themes()
    user_theme = account.themes.get_active_theme(None)

    if user_theme is None:
        return None

    try:
        if user_theme in voter_themes_available:
            has_permission = account.permissions.has_access("voter_themes")

            if has_permission or user_has_voter_perks(account.voting.load()):
                return load_theme_img(user_theme.id)

        # Theme is exclusive
        elif user_theme in account.themes.get_owned_themes():
            return load_theme_img(user_theme.id)

        return None
    except ThemeNotFoundError:
        return None


def load_background_for_user(
    discord_user_id: int,
    render_name: str,
    player_uuid_override: str | None=None,
) -> bytes | None:
    """
    Load the appropriate background image for a user.

    Providing a player UUID will override the user's Discord ID
    if there is an account linked.

    First it will attempt to find a background image, then a theme, otherwise `None`.

    :param discord_user_id: The Discord ID of the user.
    :param render_name: The name of the render to load the background for.
    :param player_uuid_override: The UUID of the player to override the Discord ID for.
    """
    bg = None

    if player_uuid_override is not None:
        linked_user_id = linking.uuid_to_discord_id(player_uuid_override)
        if linked_user_id:
            bg = load_custom_background(linked_user_id, render_name)
            bg = bg or load_user_theme(linked_user_id)

    if bg is None:
        bg = load_custom_background(discord_user_id, render_name)
        bg = bg or load_user_theme(discord_user_id)

    return bg
