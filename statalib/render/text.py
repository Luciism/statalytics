"""Text rendering utilty functions."""

from typing import Literal

from PIL import Image, ImageFont, ImageDraw

from ..assets import ASSET_LOADER
from .splitting import split_string
from ..color import ColorMappings


dummy_img = Image.new('RGBA', (0, 0))
dummy_draw = ImageDraw.Draw(dummy_img)


def calc_shadow_color(rgb: tuple) -> tuple[int, int, int]:
    """
    Calculate the drop shadow RGB value for a given RGB value.

    :param rgb: The RGB value to calculate a shadow color for.
    """
    return tuple([int(c * 0.25) for c in rgb])


def get_text_len(text: str, font: ImageFont.ImageFont):
    """
    Get the length of a string (accounting for symbols).

    :param text: The text to find the length of.
    :param font: The font to use in the calculation.
    """
    return dummy_draw.textlength(text, font=font)


def get_actual_text(text: str) -> str:
    """
    Remove color codes from text.

    :param text: The text to remove color codes from.
    :return str: The text without color codes.
    """
    split_chars = tuple(ColorMappings.color_codes)
    bits = tuple(split_string(text, split_chars))

    actual_text = ''.join([bit[0] for bit in bits])
    return actual_text


def get_start_point(
    text: str=None,
    font: ImageFont.ImageFont=None,
    align: Literal['left', 'center', 'right']='left',
    pos: int=0,
    text_len: int=None
) -> int:
    """
    Calculate the starting X position for rendering
    text with the specified settings.

    A pre-calculated text length can be provided, otherwise one will
    be calculated using the provided font.

    *__Either__ `font` and `text`, or `text_len` must be provided.*

    :param text: The text to calculate the starting X position for.
    :param font: The font that the text will be rendered in.
    :param align: The text alignment / anchor. Defaults to 'left'.
    :param pos: The relative X position. Defaults to 0.
    :param text_len: A pre-calculated custom text length.
    :return int: The calculated starting X position for the text.
    """
    assert (text, font, text_len).count(None) > 0

    if text_len is None:
        text_len = get_text_len(text, font)

    if align in ('default', 'left'):
        return pos

    if align in ('center', 'middle'):
        return round(pos - text_len / 2)

    if align == 'right':
        return round(pos - text_len)

    return 0


def render_mc_text(
    text: str,
    position: tuple[int, int],
    image: Image.Image,
    font: ImageFont.ImageFont=None,
    font_size: int=None,
    shadow_offset: tuple[int, int]=None,
    align: Literal['left', 'center', 'right']='left'
) -> int:
    """
    Renders text on an image.

    :param text: The text to draw / render.
    :param position: The (x, y) position of the text on the image.
    :param image: The image to render the text onto.
    :param font: The font to use when rendering the text.
    :param font_size: The font size to use if no font is provided.
    :param shadow_offset: The (x, y) offset of the text shadow \
        relative to the text.
    :param align: Whether to anchor the text left, right, or center.
    :return int: The final x position of the rendered text.
    """
    assert (font, font_size).count(None) > 0

    if font is None:
        font = ASSET_LOADER.load_font("main.ttf", font_size)

    split_chars = tuple(ColorMappings.color_codes)
    bits = tuple(split_string(text, split_chars))

    actual_text = ''.join([bit[0] for bit in bits])

    draw = ImageDraw.Draw(image)

    x, y = position
    x = get_start_point(
        text=actual_text,
        font=font,
        align=align,
        pos=x
    )

    for text, color_code in bits:
        color = ColorMappings.color_codes.get(color_code, ColorMappings.white)

        if shadow_offset is not None:
            off_x, off_y = shadow_offset
            shadow_color = calc_shadow_color(color)
            draw.text((x + off_x, y + off_y), text, fill=shadow_color, font=font)

        draw.text((x, y), text, fill=color, font=font)
        x += int(draw.textlength(text, font=font))

    return x
