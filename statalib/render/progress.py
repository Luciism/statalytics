from typing import Literal

from PIL import Image, ImageFont, ImageDraw

from ..assets import ASSET_LOADER
from ..common import REL_PATH
from ..calctools import PROGRESS_BAR_MAX
from .colors import get_formatted_level
from .usernames import render_level
from .text import (
    get_text_len,
    get_actual_text,
    get_start_point,
    render_mc_text
)


def render_progress_bar(
    level: int,
    xp_bar_progress: int,
    position: tuple[int, int],
    image: Image.Image,
    align: Literal['left', 'center', 'right'] = 'left'
) -> None:
    """
    Renders a progress bar for the given level and progress
    :level: The level to render the progress bar for
    :param xp_bar_progress: The progress made on the current level
    :param position: X & Y positions to render the text at
    :param image: PIL image object to render text on
    :param align: the alignment of the text relative to the x position
    """
    progress_symbol="|"
    x, y = position

    draw = ImageDraw.Draw(image)

    level_len = get_text_len(
        get_actual_text(get_formatted_level(level)), font=ASSET_LOADER.load_font("main.ttf", 20))

    target_len = get_text_len(
        get_actual_text(get_formatted_level(level+1)), font=ASSET_LOADER.load_font("main.ttf", 20))

    text_len = level_len \
        + target_len \
        + draw.textlength(f' {progress_symbol*PROGRESS_BAR_MAX} ', font=ASSET_LOADER.load_font("main.ttf", 20))

    x = get_start_point(text_len=text_len, align=align, pos=x)

    # First value (current level)
    render_level(level=level, font_size=20, image=image, position=(x, y))

    x += level_len

    # Progress bar
    colored_squares = progress_symbol * int(xp_bar_progress)
    gray_squares = progress_symbol * (PROGRESS_BAR_MAX - int(xp_bar_progress))

    # Progress bar
    x = render_mc_text(
        text=f' &b{colored_squares}&7{gray_squares} ',
        position=(x, y),
        font=ASSET_LOADER.load_font("main.ttf", 20),
        image=image,
        shadow_offset=(2, 2),
        return_x=True
    )[1]

    # Second value (next level)
    render_level(level=level+1, font_size=20, image=image, position=(x, y))


def render_progress_text(
    progress: int,
    target: int,
    position: tuple[int, int],
    image: Image.Image,
    align: Literal['left', 'center', 'right'] = 'left'
) -> Image.Image:
    """
    Render progress text: `Progress: {progress} / {target}`
    :param progress: The xp progress made on the current level
    :param target: The xp needed for the next level
    :param position: X & Y positions to render the text at
    :param image: PIL image object to render text on
    :param align: the alignment of the text relative to the x position
    """
    image = render_mc_text(
        text=f'&fProgress: &d{progress} &f/ &a{target}',
        position=position,
        font=ASSET_LOADER.load_font("main.ttf", 20),
        image=image,
        shadow_offset=(2, 2),
        align=align
    )

    return image
