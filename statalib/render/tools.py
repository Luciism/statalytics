import os
import sqlite3
from io import BytesIO
from datetime import datetime, UTC

import numpy as np
from PIL import Image, UnidentifiedImageError

from ..linking import uuid_to_discord_id
from ..cfg import config
from ..common import REL_PATH
from ..permissions import has_access
from ..themes import get_theme_properties
from .colors import Colors, get_prestige_primary_color, get_rank_color


def mc_text_shadow(rgb: tuple) -> tuple[int, int, int]:
    """
    Returns drop shadow RGB relative to passed RGB value
    :param rgb: The RGB value to get a shadow color for
    """
    return tuple([int(c * 0.25) for c in rgb])


def image_to_bytes(image: Image.Image) -> bytes:
    """
    Converts a PIL Image object to bytes
    :param image: the image object to convert to bytes
    """
    image_bytes = BytesIO()
    image.save(image_bytes, format='PNG')
    image_bytes.seek(0)

    return image_bytes


def paste_skin(
    skin_model: bytes,
    image: Image.Image,
    positions: tuple[int, int]
) -> Image.Image:
    """
    Pastes a skin onto image
    :param skin_model: the image bytes object for the skin
    :param image: the image object to paste onto
    :param positions: the X & Y coordinates to paste at
    """
    try:
        skin = Image.open(BytesIO(skin_model))
    except UnidentifiedImageError:
        skin = Image.open(f'{REL_PATH}/assets/steve_bust.png')

    composite_image = Image.new("RGBA", image.size)
    composite_image.paste(skin, positions)
    image.alpha_composite(composite_image)

    return image


def recolor_pixels(
    image: Image.Image,
    rgb_from: tuple | list,
    rgb_to: tuple | list
) -> Image.Image:
    """
    Recolors all pixels of a certain RGB value to another in an image
    :param image: The image object to recolor
    :param rgb_from: a list of RGB sets to recolor from
    :param rgb_to: a list of RGB sets to recolor to
    """
    data = np.array(image)  # "data" is a height x width x 4 numpy array
    red, green, blue, _ = data.T

    # Replace placeholder with other color... (leaves alpha values alone...)
    for rgb_from_val, rgb_to_val in zip(rgb_from, rgb_to):
        placeholders = (red == rgb_from_val[0]) & (green == rgb_from_val[1]) & (blue == rgb_from_val[2])
        data[..., :-1][placeholders.T] = rgb_to_val

    return Image.fromarray(data)


def dynamic_colored_theme(theme: str, bg_dir: str, **kwargs) -> Image.Image:
    """
    Returns image for a dynamically colored theme (mapped rank and level colors)
    :param theme: The theme you are attempting to get
    :param bg_dir: The directory that the background asset is located in
    :param **kwargs: keyword arguments should include a level and rank information
    """
    rank_info = kwargs.get('rank_info')
    level = (kwargs.get('level') // 100) * 100

    rank_color = Colors.color_codes.get(get_rank_color(rank_info))
    star_color = get_prestige_primary_color(level)

    image = Image.open(
        f'{REL_PATH}/assets/bg/{bg_dir}/themes/{theme}.png'
    ).convert('RGBA')

    rgb_from = ((213, 213, 213), (214, 214, 214))
    rgb_to = (rank_color, star_color)
    return recolor_pixels(image, rgb_from=rgb_from, rgb_to=rgb_to)


def get_theme_img(theme: str, bg_dir: str, **kwargs) -> Image:
    """
    Returns an image based on a passed theme
    :param theme: The theme you are attempting to get
    :param bg_dir: The directory that the background is located in
    :param **kwargs: any keyword arguments that may be needed for the theme
    """
    theme_properties = get_theme_properties(theme)

    if theme_properties.get('dynamic_color') is True:
        return dynamic_colored_theme(theme, bg_dir, **kwargs)

    return Image.open(f'{REL_PATH}/assets/bg/{bg_dir}/themes/{theme}.png')


def get_background(bg_dir, uuid, default='base', **kwargs) -> Image.Image:
    """
    Returns an background information based on the users setup
    :param bg_dir: The directory that the background is located in
    :param uuid: The uuid of the player who's background you are getting
    :param default: The default file name of the background (excluding .png extension)
    :param **kwargs: Any additional keyword arguments that may be used to get a background
    """
    default_path = f'{REL_PATH}/assets/bg/{bg_dir}/{default}.png'

    discord_id = uuid_to_discord_id(uuid)
    if not discord_id:
        return Image.open(default_path)

    # User has a pro subscription and a custom background
    custom_path = f'{REL_PATH}/database/custom_bg/{bg_dir}/{discord_id}.png'
    access = has_access(discord_id, 'custom_backgrounds')
    if access and os.path.exists(custom_path):
        return Image.open(custom_path)


    # Voting and rewards data for active theme pack
    with sqlite3.connect(f'{REL_PATH}/database/core.db') as conn:
        cursor = conn.cursor()

        cursor.execute(f'SELECT * FROM voting_data WHERE discord_id = {discord_id}')
        voting_data = cursor.fetchone()

        cursor.execute(f'SELECT * FROM themes_data WHERE discord_id = {discord_id}')
        themes_data = cursor.fetchone()


    # If the user has configured a theme
    if themes_data and themes_data[2]:
        voter_themes = config('global.theme_packs.voter_themes').keys()
        rewards_duration = config('global.voting.reward_duration_hours')

        # If the user has voted in the past 24 hours
        current_time = datetime.now(UTC).timestamp()

        if voting_data:
            hours_since_voted = (current_time - (voting_data[3] or 0)) / 3600
            voted_recently = voting_data and (hours_since_voted < rewards_duration)
        else:
            voted_recently = False

        theme = themes_data[2]
        if themes_data[1]:
            owned_themes = themes_data[1].split(',')

        # If the user has voted, is permission, or is using an exclusive theme
        is_exclusive = not theme in voter_themes
        if voted_recently or is_exclusive or has_access(discord_id, 'voter_themes'):
            # Check if the user is using a selected unowned exclusive theme
            if not is_exclusive or theme in owned_themes:
                try:
                    return get_theme_img(theme=theme, bg_dir=bg_dir, **kwargs)
                except FileNotFoundError:
                    pass

    return Image.open(default_path)
