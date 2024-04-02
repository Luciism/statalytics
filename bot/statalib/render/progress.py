from typing import Literal

from PIL import Image, ImageFont, ImageDraw

from ..common import REL_PATH
from .colors import get_formatted_level
from .usernames import render_level
from .text import (
    get_text_len,
    get_actual_text,
    get_start_point,
    render_mc_text
)


class Fonts:
    minecraft_13 = ImageFont.truetype(f'{REL_PATH}/assets/fonts/minecraft.ttf', 13)
    minecraft_16 = ImageFont.truetype(f'{REL_PATH}/assets/fonts/minecraft.ttf', 16)
    minecraft_20 = ImageFont.truetype(f'{REL_PATH}/assets/fonts/minecraft.ttf', 20)
    unifont_24 = ImageFont.truetype(f"{REL_PATH}/assets/fonts/unifont.ttf", 24)


def render_progress_bar(
    level: int,
    progress_of_10: int,
    position: tuple[int, int],
    image: Image.Image,
    align: Literal['left', 'center', 'right'] = 'left'
):
    """
    Renders a progress bar for the given level and progress
    :level: The level to render the progress bar for
    :param progress_of_10: The progress made on the current level out of 10
    :param position: X & Y positions to render the text at
    :param image: PIL image object to render text on
    :param align: the alignment of the text relative to the x position
    """
    x, y = position

    draw = ImageDraw.Draw(image)

    level_len = get_text_len(
        get_actual_text(get_formatted_level(level)), font=Fonts.minecraft_20)

    target_len = get_text_len(
        get_actual_text(get_formatted_level(level+1)), font=Fonts.minecraft_20)

    text_len = (level_len + target_len
        ) + draw.textlength(' [] ', font=Fonts.minecraft_13
        ) + draw.textlength('■'*10, font=Fonts.unifont_24)

    x = get_start_point(text_len=text_len, align=align, pos=x)

    # First value (current level)
    render_level(level=level, font_size=20, image=image, position=(x, y))

    x += level_len

    # Left bracket for progress bar
    x = render_mc_text(
        text=' &f[',
        position=(x, y+2),
        font=Fonts.minecraft_16,
        image=image,
        shadow_offset=(2, 2),
        return_x=True
    )[1]

    # Colored squares for progress bar
    colored_squares = "■" * int(progress_of_10)

    x = render_mc_text(
        text=f'&b{colored_squares}',
        position=(x, y-7),  # -7 to center squares vertically
        font=Fonts.unifont_24,
        image=image,
        shadow_offset=(2, 2),
        return_x=True
    )[1]


    # Gray squares for progress bar
    gray_squares = "■" * (10 - int(progress_of_10))

    x = render_mc_text(
        text=f'&7{gray_squares}',
        position=(x, y-7),  # -7 to center squares vertically
        font=Fonts.unifont_24,
        image=image,
        shadow_offset=(2, 2),
        return_x=True
    )[1] + 3  # 3 pixels padding between squares and bracket


    # Right bracket for progress bar
    x = render_mc_text(
        text='&f] ',
        position=(x, y+2),
        font=Fonts.minecraft_16,
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
        font=Fonts.minecraft_20,
        image=image,
        shadow_offset=(2, 2),
        align=align
    )

    return image
