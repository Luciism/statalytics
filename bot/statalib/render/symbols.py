from PIL import Image, ImageDraw, ImageFont

from ..functions import REL_PATH
from .colors import Colors
from .tools import mc_text_shadow


dummy_img = Image.new('RGBA', (0, 0))
dummy_draw = ImageDraw.Draw(dummy_img)


def symbol_width(
    symbol: str,
    font_size: int=None,
    font: ImageFont.ImageFont=None
) -> int:
    """
    Returns width of a symbol image
    :param symbol: the symbol to render
    :param font_size: the font size to render text
    :param font: optionally use custom font object
    """
    if font is None:
        font = ImageFont.truetype(f'{REL_PATH}/assets/fonts/unifont.ttf', font_size)

    return dummy_draw.textlength(symbol, font=font)


def render_symbol(
    image: Image.Image,
    symbol: str,
    font_size: int,
    font: ImageFont.ImageFont=None,
    position: tuple[int, int]=(0, 0),
    color: tuple[int, int, int]=Colors.white,
    shadow_offset: tuple[int, int]=None,
    return_x: bool=False
) -> Image.Image | tuple[Image.Image, int]:
    """
    Loads a symbol from and image and pastes it at the desired position
    :param image: the PIL image object to paste on
    :param symbol: the symbol to render
    :param font_size: the desired size of the symbol
    :param font: optionally use custom font object
    :param position: the x and y positions to render at
    :param color: the rgb color of the symbol
    :param shadow_offset: the text shadow offset
    :param return_x: whether or not to return the new x position
    """
    font = ImageFont.truetype(f'{REL_PATH}/assets/fonts/unifont.ttf', font_size)
    draw = ImageDraw.Draw(image)

    x, y = position

    if shadow_offset:
        off_x, off_y = shadow_offset
        shadow_color = mc_text_shadow(color)

        draw.text((x+off_x, y+off_y), symbol, fill=shadow_color, font=font)

    draw.text((x, y), symbol, fill=color, font=font)

    if return_x:
        return image, x + draw.textlength(symbol, font=font)

    return image
