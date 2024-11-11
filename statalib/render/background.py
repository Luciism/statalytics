import os
from datetime import datetime, UTC
from typing import Any, NamedTuple

from PIL import Image

from .prestige_colors import get_prestige_primary_color
from .tools import recolor_pixels
from ..assets import ASSET_LOADER
from ..cfg import config
from ..common import REL_PATH
from ..functions import db_connect
from ..linking import uuid_to_discord_id
from ..themes import get_theme_properties
from ..permissions import has_access


class VotingData(NamedTuple):
    discord_id: int
    total_votes: int
    weekend_votes: int
    last_vote: float

class ThemeData(NamedTuple):
    discord_id: int
    owned_themes: str | None
    selected_theme: str | None


def get_voting_and_theme_data(
    discord_user_id: int
) -> tuple[VotingData, ThemeData]:
    with db_connect() as conn:
        cursor = conn.cursor()

        cursor.execute(f'SELECT * FROM voting_data WHERE discord_id = {discord_user_id}')
        voting_data = cursor.fetchone()

        cursor.execute(f'SELECT * FROM themes_data WHERE discord_id = {discord_user_id}')
        themes_data = cursor.fetchone()

    return (
        VotingData(*(voting_data or (discord_user_id, 0, 0, 0))),
        ThemeData(*(themes_data or (discord_user_id, '', None))),
    )

def user_has_voter_perks(voting_data: VotingData) -> bool:
    timestamp_now = datetime.now(UTC).timestamp()
    voter_rewards_duration = config('global.voting.reward_duration_hours')

    hours_since_voted = (timestamp_now - (voting_data.last_vote)) / 3600
    return hours_since_voted < voter_rewards_duration


class RenderBackgroundTheme:
    def __init__(
        self,
        theme: str,
        dir: str,
        render_params: dict[str, Any]
    ) -> None:
        self.theme = theme
        self._asset_dir = dir
        self._render_params = render_params

        self.theme_properties = get_theme_properties(theme)
        self._theme_img_path = f"bg/{dir}/themes/{self.theme}.png"

    def _load_theme_image(self) -> Image.Image:
        return ASSET_LOADER.load_image(self._theme_img_path)

    def _load_dynamically_colored_theme(self) -> Image.Image:
        rank_info = self._render_params.get('rank_info')
        prestige = (self._render_params.get('level') // 100) * 100

        star_color = get_prestige_primary_color(prestige)

        image = self._load_theme_image().convert('RGBA')

        rgb_from = ((213, 213, 213), (214, 214, 214))
        rgb_to = (rank_info["color_rgb"], star_color)
        return recolor_pixels(image, rgb_from=rgb_from, rgb_to=rgb_to)

    def load_theme_background(self) -> Image.Image:
        if self.theme_properties.get('dynamic_color'):
            return self._load_dynamically_colored_theme()

        return self._load_theme_image()


class RenderBackground:
    def __init__(
        self,
        dir: str,
        default_filename: str="base.png"
    ) -> None:
        self._asset_dir = dir
        self._default_filename = default_filename

        self._default_img_path = f"bg/{dir}/{default_filename}"
        self._custom_img_dir = f'{REL_PATH}/database/custom_bg/{dir}/'

    def _custom_image_path(self, discord_user_id: int) -> str:
        return f"{self._custom_img_dir}/{discord_user_id}.png"

    def _user_has_custom_background(self, discord_user_id: int) -> bool:
        user_has_access = has_access(discord_user_id, 'custom_backgrounds')
        custom_path = self._custom_image_path(discord_user_id)

        return user_has_access and os.path.exists(custom_path)

    def load_default_background(self) -> Image.Image:
        return ASSET_LOADER.load_image(self._default_img_path)

    def _load_user_themed_background(
        self,
        discord_id: int,
        voting_data: VotingData,
        theme_data: ThemeData,
        render_params: dict[str, Any]
    ) -> Image.Image:
        voter_themes_available = config('global.theme_packs.voter_themes').keys()

        has_voter_perks = user_has_voter_perks(voting_data)

        owned_themes = []
        if theme_data.owned_themes is not None:
            owned_themes.extend(theme_data.owned_themes.split(","))

        selected_theme = theme_data.selected_theme
        is_theme_voter = selected_theme in voter_themes_available
        is_theme_exclusive = not is_theme_voter

        if (
            is_theme_voter and (
                has_voter_perks  # Has voter perks
                or has_access(discord_id, 'voter_themes'))  # Has access to all voter themes
            or (is_theme_exclusive and selected_theme in owned_themes)  # Owns exclusive theme
        ):
            try:
                return RenderBackgroundTheme(
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
        discord_id = uuid_to_discord_id(player_uuid)

        # Return default background if user is not linked.
        if not discord_id:
            return self.load_default_background().convert("RGBA")

        # Return custom background if the user has one.
        if self._user_has_custom_background(discord_id):
            return Image.open(self._custom_image_path(discord_id)).convert("RGBA")

        # Return the user's configured themed background
        voting_data, theme_data = get_voting_and_theme_data(discord_id)

        if theme_data.selected_theme:
            return self._load_user_themed_background(
                discord_id, voting_data, theme_data, render_params or {}
            ).convert("RGBA")

        # Return the default background
        return self.load_default_background().convert("RGBA")
