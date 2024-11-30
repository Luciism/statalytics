"""Username rendering functionality."""

from typing import Literal

from PIL import Image

from .text import render_mc_text, get_actual_text, get_text_len
from .prestige_colors import Prestige
from ..assets import ASSET_LOADER
from ..hypixel.ranks import RankInfo


def render_display_name(
    username: str,
    rank_info: RankInfo,
    image: Image.Image,
    font_size: int,
    position: tuple[int, int],
    level: int=None,
    shadow_offset: tuple[int, int]=(2, 2),
    align: Literal['left', 'center', 'right']='left',
) -> Image.Image:
    """
    Render the rank, username, and optionally the level of a player.

    :param username: The username of the respective player.
    :param rank_info: The Hypixel rank info dict of the respective player.
    :param image: The image to render the text onto.
    :param font_size: The font size to render the text with.
    :param position: The (x, y) position of the text on the image.
    :param level: The level of the respective player, or `None` in order \
        to not render the level.
    :param shadow_offset: The (x, y) offset of the text shadow relative to the text.
    :param align: Whether to align the text left, right, or center.
    """
    font = ASSET_LOADER.load_font("main.ttf", font_size)

    full_string = f'{rank_info["formatted_prefix"]}{username}'

    if level is not None:
        formatted_lvl = Prestige.format_level(level)
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
