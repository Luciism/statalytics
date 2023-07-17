from PIL import Image, ImageDraw, ImageFont

from .prestiges import get_prestige_colors
from .tools import recolor_pixels
from ..functions import REL_PATH


color_map = {
    "BLACK": (0, 0, 0),
    "DARK_BLUE": (0, 0, 170),
    "DARK_GREEN": (0, 170, 0),
    "DARK_AQUA": (0, 170, 170),
    "DARK_RED": (170, 0, 0),
    "DARK_PURPLE": (170, 0, 170),
    "GOLD": (255, 170, 0),
    "GRAY": (170, 170, 170),
    "DARK_GRAY": (85, 85, 85),
    "BLUE": (85, 85, 255),
    "GREEN": (85, 255, 85),
    "AQUA": (85, 255, 255),
    "RED": (255, 85, 85),
    "LIGHT_PURPLE": (255, 85, 255),
    "YELLOW": (255, 255, 85),
    "WHITE": (255, 255, 255)
}


def get_rank_prefix(rank_info: dict):
    """
    Returns rank prefix relative to rankinfo
    :param rank_info: Dictionary of rank info
    """

    rank = rank_info['rank']
    old_package_rank = rank_info['packageRank']
    new_package_rank = rank_info['newPackageRank']
    monthly_package_rank = rank_info['monthlyPackageRank']

    package_ranks = (old_package_rank, new_package_rank)

    if rank == "TECHNO":
        return '[PIG+++]'

    if rank in ("YOUTUBER", "ADMIN"):
        if rank == "YOUTUBER":
            return '[YOUTUBE]'
        return '[ADMIN]'

    if "VIP" in package_ranks:
        return "[VIP]"
    
    if "VIP_PLUS" in package_ranks:
        return "[VIP+]"

    if "MVP" in package_ranks:
        return "[MVP]"

    if "MVP_PLUS" in package_ranks:
        if monthly_package_rank == "NONE":
            return "[MVP+]"
        return "[MVP++]"

    return ""


def render_level(level: int, position_x: int, position_y: int,
                 fontsize: int, image: Image):
    """
    Render the star for any given level (10000+ will be red)
    :param level: The level to render
    :param position_x: The start point to render the star on
    :param position_y: The y coordinate to render the star on
    :param fontsize: The size of the font
    :param image: The image to render on
    """
    font = ImageFont.truetype(f'{REL_PATH}/assets/minecraft.ttf', fontsize)
    pos_colors = get_prestige_colors(level)
    draw = ImageDraw.Draw(image)

    star_y = round(((fontsize - 17) / 2) + position_y)
    star_type = "0_to_1000" if level < 1100 else "1100_to_2000" if level < 2100 else\
               "2100_to_3000" if level < 3100 else "3100_to_5000"

    star = Image.open(f'{REL_PATH}/assets/stars/{star_type}.png')
    star = star.convert("RGBA")
    star = recolor_pixels(
        image=star,
        rgb_from=((214, 214, 214),),
        rgb_to=(pos_colors if level < 1000 or level >= 10000 else pos_colors[5],))

    if level < 1000 or level >= 10000:
        draw.text((position_x + 2, position_y + 2), f"[{level}", fill=(0, 0, 0), font=font)
        draw.text((position_x, position_y), f'[{level}', fill=pos_colors, font=font)

        position_x += draw.textlength(f"[{level}", font=font)

        image.paste(star, (int(position_x) + 1, star_y), star)

        position_x += star.width + 2

        draw.text((position_x + 2, position_y + 2), "] ", fill=(0, 0, 0), font=font)
        draw.text((position_x, position_y), '] ', fill=pos_colors, font=font)

        position_x += draw.textlength('] ', font=font)

    elif level >= 1000:
        draw.text((position_x + 2, position_y + 2), f"[{level}", fill=(0, 0, 0), font=font)
        draw.text((position_x, position_y), '[', fill=pos_colors[0], font=font)
        position_x += draw.textlength('[', font=font)
        for i in range(4):
            draw.text((position_x, position_y), str(level)[i], fill=pos_colors[i+1], font=font)
            position_x += draw.textlength(str(level)[i], font=font)

        image.paste(star, (int(position_x) + 1, star_y), star)
        position_x += star.width + 2

        draw.text((position_x + 2, position_y + 2), "] ", fill=(0, 0, 0), font=font)
        draw.text((position_x, position_y), '] ', fill=pos_colors[6], font=font)

        position_x += draw.textlength('] ', font=font)

    return position_x


def render_rank(name: str, rank_info: dict, draw: ImageDraw, fontsize: int,
                pos_y: int, pos_x: int=None, center_x: tuple[int, int]=None):
    """
    Render prefixed rank for a specified player
    :param name: name of player
    :param rank_info: dictionary containing players rank info
    :param draw: ImageDraw object to draw with
    :param fontsize: The size of the font
    :param rank_prefix: optionally pass the rank prefix
    :param pos_y: y coordinate to start rendering at
    :param pos_x: x coordinate to start rendering at
    :param center_x: positions to center the username (box_width, box_start_x)

    either pos_x must be set or center_x must be set
    """
    font = ImageFont.truetype(f'{REL_PATH}/assets/minecraft.ttf', fontsize)

    rank = rank_info['rank']
    old_package_rank = rank_info['packageRank']
    new_package_rank = rank_info['newPackageRank']
    plus_color = rank_info['rankPlusColor']

    package_ranks = (old_package_rank, new_package_rank)
    rank_prefix = get_rank_prefix(rank_info)

    if pos_x is None:
        box_width, box_x = center_x
        totallength = draw.textlength(f'{rank_prefix}{name}', font=font)
        pos_x = round((box_width - totallength) / 2) + box_x

    if not plus_color and "VIP_PLUS" in package_ranks:
        plus_color = "GOLD"

    if rank == "TECHNO":
        plus_color = "AQUA"

    rank_color_map = {
        'PIG+++': (color_map["LIGHT_PURPLE"], color_map["LIGHT_PURPLE"]),
        'YOUTUBE': (color_map["RED"], color_map["WHITE"]),
        'ADMIN': (color_map["RED"], color_map["RED"]),
        'MVP++': (color_map["GOLD"], color_map["GOLD"]),
        'MVP': (color_map["AQUA"], color_map["AQUA"]),
        'VIP': (color_map["GREEN"], color_map["GREEN"]),
        "": (color_map["GRAY"], color_map["GRAY"])
    }

    for key, value in rank_color_map.items():
        if key in rank_prefix:
            bracket_color, rank_color = value
            rank_content = key.replace('+', '')
            break

    plusses = "+"*rank_prefix.count('+')

    if package_ranks != ("NONE", "NONE"):
        draw.text((pos_x + 2, pos_y + 2), "[", fill=color_map["BLACK"], font=font)
        draw.text((pos_x, pos_y), "[", fill=bracket_color, font=font)

        pos_x += draw.textlength("[", font=font)

        draw.text((pos_x + 2, pos_y + 2), rank_content, fill=color_map["BLACK"], font=font)
        draw.text((pos_x, pos_y), rank_content, fill=rank_color, font=font)

        pos_x += draw.textlength(rank_content, font=font)

        if plusses:
            if not plus_color:
                plus_color = "RED"
            draw.text((pos_x + 2, pos_y + 2), plusses, fill=color_map["BLACK"], font=font)
            draw.text((pos_x, pos_y), plusses, fill=color_map[plus_color], font=font)

            pos_x += draw.textlength(plusses, font=font)

        draw.text((pos_x + 2, pos_y + 2), "] ", fill=color_map["BLACK"], font=font)
        draw.text((pos_x, pos_y), "] ", fill=bracket_color, font=font)

        pos_x += draw.textlength("] ", font=font)

    draw.text((pos_x + 2, pos_y + 2), name, fill=color_map["BLACK"], font=font)
    draw.text((pos_x, pos_y), name, fill=bracket_color, font=font)



def render_level_and_name(name: str, level: int, rank_info: dict, image: Image,
                          center_x: tuple[int, int], pos_y: int, fontsize: int):
    """
    Render name with bedwars stars
    :param name: The username to render
    :param level: The star to render
    :param rank_info: The rank info to render
    :param image: The image object to rendering on
    :param center_x: positions to center the text (box_width, box_start_x)
    :param pos_y: The desired y position of the player text
    :param fontsize: The size of the font
    """
    box_width, box_x = center_x

    draw = draw = ImageDraw.Draw(image)
    font = ImageFont.truetype(f'{REL_PATH}/assets/minecraft.ttf', fontsize)

    rank_prefix = get_rank_prefix(rank_info)
    totallength = draw.textlength(f'[{level}] {rank_prefix}{name}', font=font) + 16
    pos_x = int((box_width - totallength) / 2) + box_x

    pos_x = render_level(level, pos_x, pos_y, fontsize, image)
    render_rank(name, rank_info, draw, fontsize, pos_y, pos_x=pos_x)
