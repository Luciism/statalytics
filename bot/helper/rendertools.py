import os
import time
import sqlite3
from io import BytesIO

import numpy as np
from PIL import Image, UnidentifiedImageError, ImageDraw

from .prescolor import ColorMaps
from .linking import uuid_to_discord_id
from .functions import get_subscription, get_config


def shadow(rgb: tuple) -> tuple[int, int, int]:
    """
    Returns drop shadow RGB relative to passed RGB value
    :param rgb: The RGB value to get a shadow color for
    """
    return tuple([int(c * 0.25) for c in rgb])


def box_center_text(text: str, draw: ImageDraw, box_width: int, box_start: int,
                         text_y: int, font: int, color: tuple=(255, 255, 255)) -> None:
    """
    Renders given text centered inside of a box
    :param text: The text to render
    :param draw: The ImageDraw object to draw with
    :param box_width: The width of the box to paste in
    :param box_start: The X position of the box's start
    :param text_y: The Y position to render the text at
    :param font: The ImageFont object to render the text in
    :param color: The color to render the text in (defaults to white)
    """
    totallength = draw.textlength(text, font=font)
    text_x = round((box_width - totallength) / 2) + box_start
    draw.text((text_x + 2, text_y + 2), text, fill=(0, 0, 0), font=font)
    draw.text((text_x, text_y), text, fill=color, font=font)


def paste_skin(skin_res, image: Image, positions: tuple) -> Image.Image:
    """
    Pastes a skin onto image
    :param skin_res: the image bytes object for the skin
    :param image: the image object to paste onto
    :param positions: the x & y coordinates to paste at
    """
    try:
        skin = Image.open(BytesIO(skin_res))
    except UnidentifiedImageError:
        skin = Image.open('./assets/steve.png')

    composite_image = Image.new("RGBA", image.size)
    composite_image.paste(skin, positions)
    image = Image.alpha_composite(image, composite_image)
    return image


def get_rank_color(player_rank_info: dict) -> tuple:
    """
    Returns a rank color based off of the rank information given
    :param player_rank_info: the rank information
    """
    if player_rank_info['rank'] == "TECHNO":
        rankcolor = (255, 85, 255)
    elif player_rank_info['rank'] == "NONE":
        if (player_rank_info['packageRank'], player_rank_info['newPackageRank']) == ("NONE", "NONE"):
            rankcolor = (170, 170, 170)

        elif player_rank_info['packageRank'] in ("VIP", "VIP_PLUS")\
            or player_rank_info['newPackageRank'] in ("VIP", "VIP_PLUS"):
            rankcolor = (85, 255, 85)
    
        elif player_rank_info['packageRank'] in ("MVP", "MVP_PLUS")\
            or player_rank_info['newPackageRank'] in ("MVP", "MVP_PLUS"):
            rankcolor = (85, 255, 255) if player_rank_info['monthlyPackageRank'] == "NONE" else (255, 170, 0)

    else:
        rankcolor = (255, 85, 85) if player_rank_info['rank'] in ("YOUTUBER", "ADMIN") else (0, 170, 0)
    return rankcolor


def recolor_pixels(image: Image.Image, rgb_from: tuple | list, rgb_to: tuple | list) -> Image.Image:
    """
    Recolors all pixels of a certain RGB value to another in an image
    :param image: The image object to recolor
    :param rgb_from: a list of RGB sets to recolor from
    :param rgb_to: a list of RGB sets to recolor to
    """
    data = np.array(image) # "data" is a height x width x 4 numpy array
    red, green, blue, _ = data.T

    # Replace placeholder with other color... (leaves alpha values alone...)
    for rgb_from_val, rgb_to_val in zip(rgb_from, rgb_to):
        placeholders = (red == rgb_from_val[0]) & (green == rgb_from_val[1]) & (blue == rgb_from_val[2])
        data[..., :-1][placeholders.T] = rgb_to_val

    return Image.fromarray(data)


def theme_color_sync_fusion(path: str, **kwargs) -> Image.Image:
    """
    Returns image for color sync fusion theme
    :param path: The base path of the feature location
    :param **kwargs: keyword arguments should include a level and rank information
    """
    rank_info = kwargs.get('rank_info')
    level = (kwargs.get('level') // 100) * 100

    colors = ColorMaps
    level_color = colors.color_map.get(level) if level < 1000 else colors.color_map_2.get(level)[0]
    rank_color = get_rank_color(rank_info)

    image = Image.open(f'{path}/themes/color_sync_fusion.png')
    image = image.convert('RGBA')

    rgb_from = ((213, 213, 213), (214, 214, 214))
    rgb_to = (rank_color, level_color)
    return recolor_pixels(image, rgb_from=rgb_from, rgb_to=rgb_to)


def get_theme_img(theme: str, path: str, **kwargs) -> Image:
    """
    Returns an image based on a passed theme
    :param theme: The theme you are attempting to get
    :param **kwargs: any keyword arguments that may be needed for the theme
    """
    if theme == 'color_sync_fusion':
        return theme_color_sync_fusion(path=path, **kwargs)
    else:
        return Image.open(f'{path}/themes/{theme}.png')


def get_background(path, uuid, default, **kwargs):
    """
    Returns an background information based on the users setup
    :param path: The base path of the feature location
    :param uuid: The uuid of the player who's background you are getting
    :param default: The default file name of the background (excluding .png extension)
    :param **kwargs: Any additional keyword arguments that may be used to get a background
    """
    discord_id = uuid_to_discord_id(uuid)
    if not discord_id:
        return Image.open(f'{path}/{default}.png')

    subscription = get_subscription(discord_id)
    subscription = '' if not subscription else subscription[1]

    # User has a pro subscription and a custom background
    if 'pro' in subscription and os.path.exists(f'{path}/custom/{discord_id}.png'):
        return Image.open(f'{path}/custom/{discord_id}.png')

    # Voting and rewards data for active theme pack
    with sqlite3.connect('./database/voting.db') as conn:
        cursor = conn.cursor()

        cursor.execute(f'SELECT * FROM voting_data WHERE discord_id = {discord_id}')
        voting_data = cursor.fetchone()

        cursor.execute(f'SELECT * FROM rewards_data WHERE discord_id = {discord_id}')
        rewards_data = cursor.fetchone()

        cursor.execute(f'SELECT * FROM owned_themes WHERE discord_id = {discord_id}')
        owned_themes = cursor.fetchone()

    voter_themes = get_config()['theme_packs']['voter_themes'].keys()

    # If the user has configured a theme
    if rewards_data and rewards_data[1]:
        # If the user has voted in the past 24 hours
        current_time = time.time()
        voted_recently = voting_data and ((current_time - voting_data[3]) / 3600 < 24)

        theme = rewards_data[1]
        if owned_themes:
            owned_themes = owned_themes[1].split(',')

        # If the user has voted, is premium, or is using an exclusive theme
        is_exclusive = not theme in voter_themes
        if voted_recently or subscription or is_exclusive:
            # Check if the user is using a selected unowned exclusive theme
            if not is_exclusive or theme in owned_themes:
                return get_theme_img(theme=theme, path=path, **kwargs)

    return Image.open(f'{path}/{default}.png')
