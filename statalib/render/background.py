"""Functionality responsible for loading background images."""

import os
from datetime import datetime, UTC
from typing import Any

from PIL import Image

from .prestige_colors import PrestigeColors
from .tools import recolor_pixels
from ..assets import ASSET_LOADER
from ..cfg import config
from ..common import REL_PATH
from ..accounts import uuid_to_discord_id, AccountPermissions, themes, voting


def user_has_voter_perks(voting_data: voting.VotingData) -> bool:
    """Check if a user has access to voter perks based on their voting history."""
    timestamp_now = datetime.now(UTC).timestamp()
    voter_rewards_duration = config('global.voting.reward_duration_hours')

    hours_since_voted = (timestamp_now - (voting_data.last_vote or 0)) / 3600
    return hours_since_voted < voter_rewards_duration


class ThemeImageLoader:
    """Class responsible for loading theme images."""
    def __init__(
        self,
        theme: str,
        dir: str,
        render_params: dict[str, Any]
    ) -> None:
        """
        Initialize the class with the theme name and directory.

        :param theme: The name of the theme to load.
        :param dir: The asset directory where the theme background is stored.
        :param render_params: Any custom parameters that the theme may require.
        """
        self.theme = theme
        self._asset_dir = dir
        self._render_params = render_params

        self.theme_properties = themes.get_theme_properties(theme)
        self._theme_img_path = f"bg/{dir}/themes/{self.theme}.png"

    def _load_theme_image(self) -> Image.Image:
        return ASSET_LOADER.load_image(self._theme_img_path)

    def _load_dynamically_colored_theme(self) -> Image.Image:
        rank_info = self._render_params.get('rank_info')
        prestige = (self._render_params.get('level') // 100) * 100

        star_color = PrestigeColors(prestige).primary_prestige_color

        image = self._load_theme_image().convert('RGBA')

        rgb_from = ((213, 213, 213), (214, 214, 214))
        rgb_to = (rank_info["color_rgb"], star_color)
        return recolor_pixels(image, rgb_from=rgb_from, rgb_to=rgb_to)

    def load_theme_background(self) -> Image.Image:
        """Load the theme image."""
        if self.theme_properties.get('dynamic_color'):
            return self._load_dynamically_colored_theme()

        return self._load_theme_image()


class BackgroundImageLoader:
    """Class responsible for loading background images."""
    def __init__(
        self,
        dir: str,
        default_filename: str="base.png"
    ) -> None:
        """
        Initialize the class with the background directory and default filename.

        :param dir: The asset directory where the background images are stored.
        :param default_filename: The filename of the default background image.
        """
        self._asset_dir = dir
        self._default_filename = default_filename

        self._default_img_path = f"bg/{dir}/{default_filename}"
        self._custom_img_dir = f'{REL_PATH}/database/custom_bg/{dir}/'

    def _custom_image_path(self, discord_user_id: int) -> str:
        return f"{self._custom_img_dir}/{discord_user_id}.png"

    def _user_has_custom_background(self, discord_user_id: int) -> bool:
        account_permissions = AccountPermissions(discord_user_id)
        user_has_access = account_permissions.has_access('custom_backgrounds')

        custom_path = self._custom_image_path(discord_user_id)

        return user_has_access and os.path.exists(custom_path)

    def load_default_background(self) -> Image.Image:
        """Load the default background image."""
        return ASSET_LOADER.load_image(self._default_img_path)

    def _load_user_themed_background(
        self,
        discord_id: int,
        voting_data: voting.VotingData,
        theme_data: themes.ThemesData,
        render_params: dict[str, Any]
    ) -> Image.Image:
        voter_themes_available = config('global.theme_packs.voter_themes').keys()

        has_voter_perks = user_has_voter_perks(voting_data)

        selected_theme = theme_data.active_theme
        is_theme_voter = selected_theme in voter_themes_available
        is_theme_exclusive = not is_theme_voter

        account_permissions = AccountPermissions(discord_id)

        if (
            is_theme_voter and (
                has_voter_perks  # Has voter perks
                or account_permissions.has_access('voter_themes') # Has access to all voter themes
            ) or (is_theme_exclusive and selected_theme in theme_data.owned_themes)  # Owns exclusive theme
        ):
            try:
                return ThemeImageLoader(
                    selected_theme, self._asset_dir, render_params
                ).load_theme_background()
            except FileNotFoundError:
                pass

        return self.load_default_background()


    def load_background_image(
        self,
        player_uuid: str | None=None,
        render_params: dict[str, Any]=None
    ) -> Image.Image:
        """
        Dynamically load the background image
        in accordance with the player's settings.

        :param player_uuid: The UUID of the linked player to load the background for.
        :param render_params: Any custom parameters that the theme may require.
        :return Image.Image: The loaded background image.
        """
        discord_id = uuid_to_discord_id(player_uuid)

        # Return default background if user is not linked.
        if not discord_id:
            return self.load_default_background().convert("RGBA")

        # Return custom background if the user has one.
        if self._user_has_custom_background(discord_id):
            return Image.open(self._custom_image_path(discord_id)).convert("RGBA")

        # Return the user's configured themed background
        voting_data = voting.AccountVoting(discord_id).load()
        theme_data = themes.AccountThemes(discord_id).load()

        if theme_data.active_theme:
            return self._load_user_themed_background(
                discord_id, voting_data, theme_data, render_params or {}
            ).convert("RGBA")

        # Return the default background
        return self.load_default_background().convert("RGBA")
