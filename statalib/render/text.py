from typing import Literal

from PIL import Image, ImageFont, ImageDraw

from ..common import REL_PATH
from .splitting import split_string, split_at_symbols
from .colors import Colors
from .tools import mc_text_shadow
from .symbols import render_symbol, symbol_width, dummy_draw


def get_text_len(text: str, font: ImageFont.ImageFont):
    """
    Get the length of a string accounting for symbols
    :param text: the text to find the length of
    :param font: the primary font for the text to be in
    """
    text_len = 0

    text_dicts = split_at_symbols(text)

    for text_dict in text_dicts:
        value = text_dict.get('value')

        if text_dict.get('type') == 'text':
            text_len += dummy_draw.textlength(value, font=font)

        elif text_dict.get('type') == 'symbol':
            text_len += symbol_width(value, font.size)

    return text_len


def get_actual_text(text: str) -> str:
    """
    Returns text with color codes removed
    :param text: the text to clean
    """
    split_chars = tuple(Colors.color_codes)
    bits = tuple(split_string(text, split_chars))

    actual_text = ''.join([bit[0] for bit in bits])
    return actual_text


def get_start_point(
    text: str=None,
    font: ImageFont.ImageFont=None,
    align: Literal['left', 'center', 'right']='left',
    pos: int=None,
    text_len: int=None
) -> int:
    """
    Returns the x position to render text with desired settings

    A pre-determined text length can be provided otherwise one will
    be calculated with the provided font. Either `font` and `text`
    or `text_len` must be provided.
    :param text: The text to find the start point of
    :param font: The font of the text
    :param align: The relative text alignment. Defaults to 'left'.
    :param pos: The x position of the text. Defaults to None.
    :param text_len: pre-determined custom text length
    """
    assert (text, font, text_len).count(None) > 0

    if text_len is None:
        text_len = get_text_len(text, font)

    if pos is None:
        return 0

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
    align: Literal['left', 'center', 'right']='left',
    return_x: bool=False
) -> Image.Image | tuple[Image.Image, int]:
    """
    :param text: Text to render on the image
    :param position: X & Y positions to render the text at
    :param image: PIL image object to render text on
    :param font: Font used to render text
    :param font_size: The fontsize to use if no font object is passed
    :param shadow_offset: X & Y positions to offset the drop shadow
    :param align: the alignment of the text relative to the x position
    :param return_x: whether or not to return the new x position
    """
    assert (font, font_size).count(None) > 0

    if font is None:
        font = ImageFont.truetype(
            f'{REL_PATH}/assets/fonts/minecraft.ttf', size=font_size)

    split_chars = tuple(Colors.color_codes)
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
        color = Colors.color_codes.get(color_code, Colors.white)

        text_dicts = split_at_symbols(text)

        for text_dict in text_dicts:
            value = text_dict.get('value')
            if text_dict.get('type') == 'symbol':
                image, x = render_symbol(
                    image=image,
                    symbol=value,
                    position=(x, y),
                    font_size=font.size,
                    color=color,
                    shadow_offset=shadow_offset,
                    return_x=True
                )

            elif text_dict.get('type') == 'text':
                if shadow_offset is not None:
                    off_x, off_y = shadow_offset
                    shadow_color = mc_text_shadow(color)
                    draw.text((x + off_x, y + off_y), value, fill=shadow_color, font=font)

                draw.text((x, y), value, fill=color, font=font)

                x += int(draw.textlength(value, font=font))

    if return_x:
        return image, x

    return image
