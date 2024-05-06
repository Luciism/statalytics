from typing import Literal

from PIL import Image, ImageFont

from .text import render_mc_text, get_actual_text, get_text_len
from .colors import Colors, get_formatted_level
from ..assets import ASSET_LOADER
from ..common import REL_PATH


def get_rank_prefix(rank_info: dict):
    """
    Returns rank prefix relative to rankinfo
    :param rank_info: Dictionary of rank info
    """
    rank = rank_info['rank']
    old_package_rank = rank_info['packageRank']
    new_package_rank = rank_info['newPackageRank']
    monthly_package_rank = rank_info['monthlyPackageRank']

    plus_color: str = rank_info['rankPlusColor']

    if plus_color is not None:
        plus_color_code = Colors.str_to_color_code.get(plus_color.lower())
    else:
        plus_color_code = Colors.str_to_color_code.get('red')


    package_ranks = (old_package_rank, new_package_rank)

    if rank == 'TECHNO':
        return '&d[PIG&b+++&d] '

    if rank in ('YOUTUBER', 'ADMIN'):
        if rank == 'YOUTUBER':
            return '&c[&fYOUTUBE&c] '
        return '&c[ADMIN] '

    if 'VIP' in package_ranks:
        return '&a[VIP] '

    if 'VIP_PLUS' in package_ranks:
        return '&a[VIP&6+&a] '

    if 'MVP' in package_ranks:
        return '&b[MVP] '

    if 'MVP_PLUS' in package_ranks:
        if monthly_package_rank == 'NONE':
            return f'&b[MVP{plus_color_code}+&b] '
        return f'&6[MVP{plus_color_code}++&6] '

    return '&7'


def render_level(
    level: int,
    font_size: int,
    image: Image.Image,
    position: tuple[int, int],
    shadow_offset=(2, 2),
    align: Literal['left', 'center', 'right']='left',
) -> int:
    """
    Render the star for any given level (10000+ will be red)
    :param level: The level to render
    :param font_size: The size of the font
    :param image: The image to render on
    :param position: X & Y positions to render the text at
    :param shadow_offset: X & Y positions to offset the drop shadow
    :param align: the alignment of the text relative to the x position
    :return: the final x position once the level has been rendered
    """
    formatted_lvl_str = get_formatted_level(level)
    image, x_after = render_mc_text(
        text=formatted_lvl_str,
        position=position,
        font=ASSET_LOADER.load_font("main.ttf", font_size),
        image=image,
        shadow_offset=shadow_offset,
        align=align,
        return_x=True
    )

    return x_after


def render_display_name(
    username: str,
    rank_info: dict,
    image: Image.Image,
    font_size: int,
    position: tuple[int, int],
    level: int=None,
    shadow_offset: tuple[int, int]=(2, 2),
    align: Literal['left', 'center', 'right']='left',
) -> Image.Image:
    """
    Render prefixed rank for a specified player
    :param username: the username of the respective player
    :param rank_info: dictionary containing the players rank info
    :param image: The image to render on
    :param font_size: The size of the font to render with
    :param position: X & Y positions to render the text at
    :param level: if `None`, no level is rendered
    :param shadow_offset: X & Y positions to offset the drop shadow
    :param align: the alignment of the text relative to the x position
    """
    font = ASSET_LOADER.load_font("main.ttf", font_size)

    rank_prefix = get_rank_prefix(rank_info)
    full_string = f'{rank_prefix}{username}'

    if level is not None:
        formatted_lvl = get_formatted_level(level)
        full_string = f'{formatted_lvl} {full_string}'

    if image is None:
        text_len = get_text_len(get_actual_text(full_string), font)
        # additional 20 pixels for padding
        image = Image.new('RGBA', (int(text_len) + 20, font_size), (0, 0, 0, 0))

        x, y = position
        x = image.width / 2
        position = (x, y)

    render_mc_text(
        text=full_string,
        position=position,
        font=font,
        image=image,
        shadow_offset=shadow_offset,
        align=align
    )

    return image
