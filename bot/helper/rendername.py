from PIL import Image, ImageDraw, ImageFont

from helper.prescolor import get_prestige_colors
from helper.rendertools import recolor_pixels


def get_color_map():
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
    return color_map

def get_rank_prefix(player_rank_info: dict):
    """
    Returns rank prefix relative to rankinfo
    :param player_rank_info: Dictionary of rank info
    """

    rank, old_package_rank, new_package_rank, monthly_package_rank, _ = player_rank_info.values()

    if rank == "TECHNO":
        rank_prefix = '[PIG+++]'
    elif rank in ("YOUTUBER", "ADMIN"):
        rank_prefix = '[YOUTUBE]' if rank == "YOUTUBER" else '[ADMIN]'
    elif old_package_rank in ("VIP", "VIP_PLUS") or new_package_rank in ("VIP", "VIP_PLUS"):
        rank_prefix = "[VIP]" if old_package_rank == "VIP" or new_package_rank == "VIP" else "[VIP+]"
    elif old_package_rank in ("MVP", "MVP_PLUS") or new_package_rank in ("MVP", "MVP_PLUS"):
        rank_prefix = "[MVP]" if old_package_rank == "MVP" or new_package_rank == "MVP" else "[MVP+]" if monthly_package_rank == "NONE" else "[MVP++]"
    else:
        rank_prefix = ""

    return rank_prefix

def render_level(level: int, position_x: int, position_y: int, fontsize: int, image: Image):
    """
    Render the star for any given level (10000+ will be red)
    :param level: The level to render
    :param position_x: The start point to render the star on
    :param position_y: The y coordinate to render the star on
    :param fontsize: The size of the font
    :param image: The image to render on
    """
    font = ImageFont.truetype('./assets/minecraft.ttf', fontsize)
    pos_colors = get_prestige_colors(level)
    draw = ImageDraw.Draw(image)

    star_y = round(((fontsize - 17) / 2) + position_y)
    star_type = "0_to_1000" if level < 1100 else "1100_to_2000" if level < 2100 else\
               "2100_to_3000" if level < 3100 else "3100_to_5000"
    star = Image.open(f'./assets/stars/{star_type}.png')
    star = star.convert("RGBA")
    star = recolor_pixels(star, ((214, 214, 214),), (pos_colors if level < 1000 else pos_colors[5],))

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

def render_rank(name: str, position_x: int, position_y: int, rank_prefix: str, player_rank_info: dict, draw: ImageDraw, fontsize: int):
    """
    Render prefixed rank for a specified player
    :param name: name of player
    :param position_x: x coordinate to render at
    :param position_y: y coordinate to render at
    :param rank_prefix: players rank prefix
    :param player_rank_info: dictionary containing players rank info
    :param draw: ImageDraw object to draw with
    :param fontsize: The size of the font
    """

    font = ImageFont.truetype('./assets/minecraft.ttf', fontsize)
    color_map = get_color_map()

    rank = player_rank_info['rank']
    old_package_rank = player_rank_info['packageRank']
    new_package_rank = player_rank_info['newPackageRank']
    plus_color = player_rank_info['rankPlusColor']

    plus_color = plus_color if plus_color else "GOLD" if "VIP_PLUS" in (old_package_rank, new_package_rank) else None
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

    if (old_package_rank, new_package_rank) != ("NONE", "NONE"):
        draw.text((position_x + 2, position_y + 2), "[", fill=color_map["BLACK"], font=font)
        draw.text((position_x, position_y), "[", fill=bracket_color, font=font)

        position_x += draw.textlength("[", font=font)

        draw.text((position_x + 2, position_y + 2), rank_content, fill=color_map["BLACK"], font=font)
        draw.text((position_x, position_y), rank_content, fill=rank_color, font=font)

        position_x += draw.textlength(rank_content, font=font)

        if plusses:
            if not plus_color:
                plus_color = "RED"
            draw.text((position_x + 2, position_y + 2), plusses, fill=color_map["BLACK"], font=font)
            draw.text((position_x, position_y), plusses, fill=color_map[plus_color], font=font)

            position_x += draw.textlength(plusses, font=font)

        draw.text((position_x + 2, position_y + 2), "] ", fill=color_map["BLACK"], font=font)
        draw.text((position_x, position_y), "] ", fill=bracket_color, font=font)

        position_x += draw.textlength("] ", font=font)

    draw.text((position_x + 2, position_y + 2), name, fill=color_map["BLACK"], font=font)
    draw.text((position_x, position_y), name, fill=bracket_color, font=font)

def render_level_and_name(name: str, level: int, player_rank_info: dict, image: Image, box_positions: tuple, position_y: int, fontsize: int):
    """
    Render name with bedwars stars
    :param name: The name of the player
    :param level: The star of the player
    :param player_rank_info: The rank info of the player
    :param image: The image you are rendering on
    :param box_positions: The box positions relative to the render position
    :param position_y: The desired y position of the player text
    :param fontsize: The size of the font
    """

    box_x, box_width = box_positions

    draw = draw = ImageDraw.Draw(image)
    font = ImageFont.truetype('./assets/minecraft.ttf', fontsize)

    rank_prefix = get_rank_prefix(player_rank_info)
    totallength = draw.textlength(f'[{level}] {rank_prefix}{name}', font=font) + 16
    position_x = int((box_width - totallength) / 2) + box_x

    position_x = render_level(level, position_x, position_y, fontsize, image)
    render_rank(name, position_x, position_y, rank_prefix, player_rank_info, draw, fontsize)
