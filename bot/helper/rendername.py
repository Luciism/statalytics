import os
from PIL import Image, ImageDraw, ImageFont
from helper.prescolor import Prescolor

def render_name(name, level, playerrank, image, player_y, fontsize):
    """
    Render name with bedwars stars
    :name: The name of the player
    :level: The star of the player
    :playerrank: The rank info of the player
    :image: The image you are rendering on
    :player_y: The desired y position of the player text
    :fontsize: The size of the font
    """
    white = (255, 255, 255)
    red = (255, 76, 76)
    black = (0, 0, 0)
    gold = (255, 170, 0)

    pos1, pos2, pos3, pos4, pos5, pos6, pos7 = Prescolor(level).get_level_color()


    draw = draw = ImageDraw.Draw(image)
    font = ImageFont.truetype(f'{os.getcwd()}/assets/minecraft.ttf', fontsize)

    star = Image.open(f'{os.getcwd()}/assets/stars/{pos6}.png')
    star_black = Image.open(f'{os.getcwd()}/assets/stars/black.png')

    # Convert
    star = star.convert("RGBA")
    star_black = star_black.convert("RGBA")

    if playerrank['rank'] in ("YOUTUBER", "ADMIN"):
        rankstuff = '[YOUTUBE]' if playerrank['rank'] == "YOUTUBER" else '[ADMIN]'
    elif playerrank['packageRank'] in ("VIP", "VIP_PLUS") or playerrank['newPackageRank'] in ("VIP", "VIP_PLUS"):
        rankstuff = "[VIP]" if playerrank['packageRank'] == "VIP" else "[VIP+]"
    elif playerrank['packageRank'] in ("MVP", "MVP_PLUS") or playerrank['newPackageRank'] in ("MVP", "MVP_PLUS"):
        rankstuff = "[MVP]" if playerrank['packageRank'] == "MVP" else "[MVP+]" if playerrank['monthlyPackageRank'] == "NONE" else "[MVP++]"
    else:
        rankstuff = ""

    totallength = star.width + draw.textlength(f'[{level}] ', font=font) + draw.textlength(name, font=font) + draw.textlength(rankstuff, font=font)
    startpoint = int((image.width - totallength) / 2)

    if level < 1000 or level >= 10000:
        draw.text((startpoint + 2, player_y + 2), f"[{level}", fill=black, font=font)
        draw.text((startpoint, player_y), f'[{level}', fill=pos1, font=font)

        startpoint += draw.textlength(f"[{level}", font=font)

        image.paste(star_black, (int(startpoint) + 3, player_y + 2), star_black)
        image.paste(star, (int(startpoint) + 1, player_y + 1), star)

        startpoint += star.width + 2

        draw.text((startpoint + 2, player_y + 2), "] ", fill=black, font=font)
        draw.text((startpoint, player_y), '] ', fill=pos1, font=font)

        startpoint += draw.textlength('] ', font=font)

    elif level >= 1000:
        draw.text((startpoint + 2, player_y + 2), f"[{level}", fill=black, font=font)
        draw.text((startpoint, player_y), '[', fill=pos1, font=font)
        startpoint += draw.textlength('[', font=font)

        draw.text((startpoint, player_y), str(level)[0], fill=pos2, font=font)
        startpoint += draw.textlength(str(level)[0], font=font)

        draw.text((startpoint, player_y), str(level)[1], fill=pos3, font=font)
        startpoint += draw.textlength(str(level)[1], font=font)

        draw.text((startpoint, player_y), str(level)[2], fill=pos4, font=font)
        startpoint += draw.textlength(str(level)[2], font=font)

        draw.text((startpoint, player_y), str(level)[3], fill=pos5, font=font)
        startpoint += draw.textlength(str(level)[3], font=font)

        image.paste(star_black, (int(startpoint) + 3, player_y + 2), star_black)
        image.paste(star, (int(startpoint) + 1, player_y + 1), star)
        startpoint += star.width + 2

        draw.text((startpoint + 2, player_y + 2), "] ", fill=black, font=font)
        draw.text((startpoint, player_y), '] ', fill=pos7, font=font)

        startpoint += draw.textlength('] ', font=font)

    if playerrank['rank'] == "NONE":
        if playerrank['packageRank'] == "NONE" and playerrank['newPackageRank'] == "NONE":
            rankcolor = (170, 170, 170)
        elif playerrank['packageRank'] == "VIP" or playerrank['newPackageRank'] == "VIP":
            rankcolor = (85, 255, 85)
            draw.text((startpoint + 2, player_y + 2), "[VIP] ", fill=black, font=font)
            draw.text((startpoint, player_y), "[VIP] ", fill=rankcolor, font=font)
            startpoint += draw.textlength("[VIP] ", font=font)

        elif playerrank['packageRank'] == "VIP_PLUS" or playerrank['newPackageRank'] == "VIP_PLUS":
            rankcolor = (85, 255, 85)
            draw.text((startpoint + 2, player_y + 2), "[VIP ", fill=black, font=font)
            draw.text((startpoint, player_y), "[VIP ", fill=rankcolor, font=font)
            startpoint += draw.textlength("[VIP ", font=font)

            draw.text((startpoint + 2, player_y + 2), "+", fill=black, font=font)
            draw.text((startpoint, player_y), "+", fill=gold, font=font)
            startpoint += draw.textlength("+", font=font)

            draw.text((startpoint + 2, player_y + 2), "] ", fill=black, font=font)
            draw.text((startpoint, player_y), "] ", fill=rankcolor, font=font)
            startpoint += draw.textlength("] ", font=font)

        elif playerrank['packageRank'] == "MVP_PLUS" or playerrank['newPackageRank'] == "MVP_PLUS" or playerrank['packageRank'] == "MVP" or playerrank['newPackageRank'] == "MVP":
            bukkit_colors = {"BLACK": (0, 0, 0), "DARK_BLUE": (0, 0, 170), "DARK_GREEN": (0, 170, 0), "DARK_AQUA": (0, 170, 170), "DARK_RED": (170, 0, 0), "DARK_PURPLE": (170, 0, 170), "GOLD": (255, 170, 0), "GRAY": (170, 170, 170), "DARK_GRAY": (85, 85, 85), "BLUE": (85, 85, 255), "GREEN": (85, 255, 85), "AQUA": (85, 255, 255), "RED": (255, 85, 85), "LIGHT_PURPLE": (255, 85, 255), "YELLOW": (255, 255, 85), "WHITE": (255, 255, 255)}
            for color, (r, g, b) in bukkit_colors.items():
                if playerrank['rankPlusColor'] == color:
                    pluscolor = (r, g, b)
                    break
            else:
                pluscolor = (255, 85, 85)
            if playerrank['monthlyPackageRank'] == "NONE":
                rankcolor = (85, 255, 255)
                plusses = "+"
            else:
                rankcolor = (255, 170, 0)
                plusses = "++"
            draw.text((startpoint + 2, player_y + 2), "[MVP", fill=black, font=font)
            draw.text((startpoint, player_y), "[MVP", fill=rankcolor, font=font)
            startpoint += draw.textlength("[MVP", font=font)

            if playerrank['packageRank'] == "MVP_PLUS" or playerrank['newPackageRank'] == "MVP_PLUS":
                draw.text((startpoint + 2, player_y + 2), plusses, fill=black, font=font)
                draw.text((startpoint, player_y), plusses, fill=pluscolor, font=font)
                startpoint += draw.textlength(plusses, font=font)

            draw.text((startpoint + 2, player_y + 2), "] ", fill=black, font=font)
            draw.text((startpoint, player_y), "] ", fill=rankcolor, font=font)
            startpoint += draw.textlength("] ", font=font)
    elif playerrank['rank'] == "YOUTUBER" or playerrank['rank'] == "ADMIN":
        rankcolor = (255, 85, 85)
        draw.text((startpoint + 2, player_y + 2), "[", fill=black, font=font)
        draw.text((startpoint, player_y), "[", fill=red, font=font)
        startpoint += draw.textlength("[", font=font)

        if playerrank['rank'] == "YOUTUBER":
            draw.text((startpoint + 2, player_y + 2), 'YOUTUBE', fill=black, font=font)
            draw.text((startpoint, player_y), 'YOUTUBE', fill=white, font=font)
            startpoint += draw.textlength('YOUTUBE', font=font)
        elif playerrank['rank'] == "ADMIN":
            draw.text((startpoint + 2, player_y + 2), 'ADMIN', fill=black, font=font)
            draw.text((startpoint, player_y), 'ADMIN', fill=red, font=font)
            startpoint += draw.textlength('ADMIN', font=font)

        draw.text((startpoint + 2, player_y + 2), "] ", fill=black, font=font)
        draw.text((startpoint, player_y), "] ", fill=red, font=font)
        startpoint += draw.textlength("] ", font=font)
    else:
        rankcolor = (170, 170, 170)

    draw.text((startpoint + 2, player_y + 2), name, fill=black, font=font)
    draw.text((startpoint, player_y), name, fill=rankcolor, font=font)

def render_level(level, image, startpoint, startpoint_y, fontsize):
    """
    Render the star for any given level (10000+ will be red)
    :level: The level to render
    :image: The image to render on
    :startpoint: The start point to render the star on
    :startpoint_y: The y coordinate to render the star on
    :fontsize: The size of the font
    """
    star_y = int(startpoint_y + ((fontsize - 16) / 2) - (fontsize / 10))

    black = (0, 0, 0)

    pos1, pos2, pos3, pos4, pos5, pos6, pos7 = Prescolor(level).get_level_color()


    draw = draw = ImageDraw.Draw(image)
    font = ImageFont.truetype(f'{os.getcwd()}/assets/minecraft.ttf', fontsize)

    # Stars
    star = Image.open(f'{os.getcwd()}/assets/stars/{pos6}.png')
    star_black = Image.open(f'{os.getcwd()}/assets/stars/black.png')

    star = star.convert("RGBA")
    star_black = star_black.convert("RGBA")

    if level < 1000 or level >= 10000:
        draw.text((startpoint + 2, startpoint_y + 2), f"[{level}", fill=black, font=font)
        draw.text((startpoint, startpoint_y), f'[{level}', fill=pos1, font=font)

        startpoint += draw.textlength(f"[{level}", font=font)

        image.paste(star_black, (int(startpoint) + 3, star_y + 2), star_black)
        image.paste(star, (int(startpoint) + 1, star_y + 1), star)

        startpoint += star.width + 2

        draw.text((startpoint + 2, startpoint_y + 2), "] ", fill=black, font=font)
        draw.text((startpoint, startpoint_y), '] ', fill=pos1, font=font)

    elif level >= 1000:
        draw.text((startpoint + 2, startpoint_y + 2), f"[{level}", fill=black, font=font)
        draw.text((startpoint, startpoint_y), '[', fill=pos1, font=font)
        startpoint += draw.textlength('[', font=font)

        draw.text((startpoint, startpoint_y), str(level)[0], fill=pos2, font=font)
        startpoint += draw.textlength(str(level)[0], font=font)

        draw.text((startpoint, startpoint_y), str(level)[1], fill=pos3, font=font)
        startpoint += draw.textlength(str(level)[1], font=font)

        draw.text((startpoint, startpoint_y), str(level)[2], fill=pos4, font=font)
        startpoint += draw.textlength(str(level)[2], font=font)

        draw.text((startpoint, startpoint_y), str(level)[3], fill=pos5, font=font)
        startpoint += draw.textlength(str(level)[3], font=font)

        image.paste(star_black, (int(startpoint) + 3, star_y + 2), star_black)
        image.paste(star, (int(startpoint) + 1, star_y + 1), star)
        startpoint += star.width + 2

        draw.text((startpoint + 2, startpoint_y + 2), "] ", fill=black, font=font)
        draw.text((startpoint, startpoint_y), '] ', fill=pos7, font=font)


def rank_color(player_rank):
    """
    Returns a rank color based off of the rank information given
    :player_rank: the rank information
    """
    if player_rank['rank'] == "NONE":
        if (player_rank['packageRank'], player_rank['newPackageRank']) == ("NONE", "NONE"):
            rankcolor = (170, 170, 170)
        elif player_rank['packageRank'] in ("VIP", "VIP_PLUS") or player_rank['newPackageRank'] in ("VIP", "VIP_PLUS"):
            rankcolor = (85, 255, 85)
        elif player_rank['packageRank'] in ("MVP", "MVP_PLUS") or player_rank['newPackageRank'] in ("MVP", "MVP_PLUS"):
            rankcolor = (85, 255, 255) if player_rank['monthlyPackageRank'] == "NONE" else (255, 170, 0)
    else:
        rankcolor = (255, 85, 85) if player_rank['rank'] in ("YOUTUBER", "ADMIN") else (0, 170, 0)
    return rankcolor

def render_name_rank_only(name: str, playerrank: dict, image: Image, box_x: int, box_width: int, player_y: int, fontsize: int):
    """
    Render the name and rank of a player
    :name: Name of the player (case sensitive)
    :playerrank: Rank information of the player
    :image: Image to draw on
    :box_x: X position of the box
    box_width: Width of the box
    :player_y: Y position of the player text
    :fontsize: Font size of the player text
    """

    white = (255, 255, 255)
    red = (255, 76, 76)
    black = (0, 0, 0)
    gold = (255, 170, 0)

    draw = ImageDraw.Draw(image)
    font = ImageFont.truetype(f'{os.getcwd()}/assets/minecraft.ttf', fontsize)

    if playerrank['rank'] in ("YOUTUBER", "ADMIN"):
        rankstuff = '[YOUTUBE]' if playerrank['rank'] == "YOUTUBER" else '[ADMIN]'
    elif playerrank['packageRank'] in ("VIP", "VIP_PLUS") or playerrank['newPackageRank'] in ("VIP", "VIP_PLUS"):
        rankstuff = "[VIP]" if playerrank['packageRank'] == "VIP" else "[VIP+]"
    elif playerrank['packageRank'] in ("MVP", "MVP_PLUS") or playerrank['newPackageRank'] in ("MVP", "MVP_PLUS"):
        rankstuff = "[MVP]" if playerrank['packageRank'] == "MVP" else "[MVP+]" if playerrank['monthlyPackageRank'] == "NONE" else "[MVP++]"
    else:
        rankstuff = ""

    totallength = draw.textlength(name, font=font) + draw.textlength(rankstuff, font=font)
    startpoint = int((box_width - totallength) / 2) + box_x

    if playerrank['rank'] == "NONE":
        if playerrank['packageRank'] == "NONE" and playerrank['newPackageRank'] == "NONE":
            rankcolor = (170, 170, 170)
        elif playerrank['packageRank'] == "VIP" or playerrank['newPackageRank'] == "VIP":
            rankcolor = (85, 255, 85)
            draw.text((startpoint + 2, player_y + 2), "[VIP] ", fill=black, font=font)
            draw.text((startpoint, player_y), "[VIP] ", fill=rankcolor, font=font)
            startpoint += draw.textlength("[VIP] ", font=font)

        elif playerrank['packageRank'] == "VIP_PLUS" or playerrank['newPackageRank'] == "VIP_PLUS":
            rankcolor = (85, 255, 85)
            draw.text((startpoint + 2, player_y + 2), "[VIP ", fill=black, font=font)
            draw.text((startpoint, player_y), "[VIP ", fill=rankcolor, font=font)
            startpoint += draw.textlength("[VIP ", font=font)

            draw.text((startpoint + 2, player_y + 2), "+", fill=black, font=font)
            draw.text((startpoint, player_y), "+", fill=gold, font=font)
            startpoint += draw.textlength("+", font=font)

            draw.text((startpoint + 2, player_y + 2), "] ", fill=black, font=font)
            draw.text((startpoint, player_y), "] ", fill=rankcolor, font=font)
            startpoint += draw.textlength("] ", font=font)

        elif playerrank['packageRank'] == "MVP_PLUS" or playerrank['newPackageRank'] == "MVP_PLUS" or playerrank['packageRank'] == "MVP" or playerrank['newPackageRank'] == "MVP":
            bukkit_colors = {"BLACK": (0, 0, 0), "DARK_BLUE": (0, 0, 170), "DARK_GREEN": (0, 170, 0), "DARK_AQUA": (0, 170, 170), "DARK_RED": (170, 0, 0), "DARK_PURPLE": (170, 0, 170), "GOLD": (255, 170, 0), "GRAY": (170, 170, 170), "DARK_GRAY": (85, 85, 85), "BLUE": (85, 85, 255), "GREEN": (85, 255, 85), "AQUA": (85, 255, 255), "RED": (255, 85, 85), "LIGHT_PURPLE": (255, 85, 255), "YELLOW": (255, 255, 85), "WHITE": (255, 255, 255)}
            for color, (r, g, b) in bukkit_colors.items():
                if playerrank['rankPlusColor'] == color:
                    pluscolor = (r, g, b)
                    break
            else:
                pluscolor = (255, 85, 85)
            if playerrank['monthlyPackageRank'] == "NONE":
                rankcolor = (85, 255, 255)
                plusses = "+"
            else:
                rankcolor = (255, 170, 0)
                plusses = "++"
            draw.text((startpoint + 2, player_y + 2), "[MVP", fill=black, font=font)
            draw.text((startpoint, player_y), "[MVP", fill=rankcolor, font=font)
            startpoint += draw.textlength("[MVP", font=font)

            if playerrank['packageRank'] == "MVP_PLUS" or playerrank['newPackageRank'] == "MVP_PLUS":
                draw.text((startpoint + 2, player_y + 2), plusses, fill=black, font=font)
                draw.text((startpoint, player_y), plusses, fill=pluscolor, font=font)
                startpoint += draw.textlength(plusses, font=font)

            draw.text((startpoint + 2, player_y + 2), "] ", fill=black, font=font)
            draw.text((startpoint, player_y), "] ", fill=rankcolor, font=font)
            startpoint += draw.textlength("] ", font=font)
    elif playerrank['rank'] == "YOUTUBER" or playerrank['rank'] == "ADMIN":
        rankcolor = (255, 85, 85)
        draw.text((startpoint + 2, player_y + 2), "[", fill=black, font=font)
        draw.text((startpoint, player_y), "[", fill=red, font=font)
        startpoint += draw.textlength("[", font=font)

        if playerrank['rank'] == "YOUTUBER":
            draw.text((startpoint + 2, player_y + 2), 'YOUTUBE', fill=black, font=font)
            draw.text((startpoint, player_y), 'YOUTUBE', fill=white, font=font)
            startpoint += draw.textlength('YOUTUBE', font=font)
        elif playerrank['rank'] == "ADMIN":
            draw.text((startpoint + 2, player_y + 2), 'ADMIN', fill=black, font=font)
            draw.text((startpoint, player_y), 'ADMIN', fill=red, font=font)
            startpoint += draw.textlength('ADMIN', font=font)

        draw.text((startpoint + 2, player_y + 2), "] ", fill=black, font=font)
        draw.text((startpoint, player_y), "] ", fill=red, font=font)
        startpoint += draw.textlength("] ", font=font)
    else:
        rankcolor = (170, 170, 170)

    draw.text((startpoint + 2, player_y + 2), name, fill=black, font=font)
    draw.text((startpoint, player_y), name, fill=rankcolor, font=font)
