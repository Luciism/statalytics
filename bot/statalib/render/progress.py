# FIXME: redo this whole ass file
from PIL import Image, ImageFont, ImageDraw

from .usernames import render_level
from ..functions import REL_PATH


class Values:
    minecraft_13 = ImageFont.truetype(f'{REL_PATH}/assets/minecraft.ttf', 13)
    minecraft_16 = ImageFont.truetype(f'{REL_PATH}/assets/minecraft.ttf', 16)
    minecraft_20 = ImageFont.truetype(f'{REL_PATH}/assets/minecraft.ttf', 20)
    minecraft_22 = ImageFont.truetype(f'{REL_PATH}/assets/minecraft.ttf', 22)
    arial_24 = ImageFont.truetype(f"{REL_PATH}/assets/arial.ttf", 24)

    white = (255, 255, 255)
    black = (0, 0, 0)
    aqua = (85, 255, 255)
    gray = (170, 170, 170)
    light_purple = (255, 85, 255)
    green = (85, 255, 85)


def render_progress_bar(box_positions: tuple, position_y: int,
                        level: int, progress_out_of_10: int, image: Image):
    """
    :param box_positions: Values for container to center the progress bar (box_width, box_start_x)
    :param position_y: Y position to render the progress bar
    :level: The current level of the player
    :param progress_out_of_10: The progress made on the current level out of 10
    :param image: The Image object that is being drawn on
    """

    draw = ImageDraw.Draw(image)

    # Render the progress
    totallength = draw.textlength(f'[{level}][{level + 1}]', font=Values.minecraft_20
                                  ) + draw.textlength(' [] ', font=Values.minecraft_13
                                  ) + draw.textlength('■■■■■■■■■■', font=Values.arial_24
                                  ) + 44 # 44 for star and centering

    startpoint = int((box_positions[0] - totallength) / 2) + box_positions[1]

    # First value (current level)
    render_level(
        level=level,
        font_size=20,
        image=image,
        position=(startpoint, position_y),
    )

    startpoint += draw.textlength(f'[{level}]', font=Values.minecraft_20) + 16

    # Left bracket for bar
    draw.text((startpoint + 2, position_y + 3), "  [", fill=Values.black, font=Values.minecraft_16)
    draw.text((startpoint, position_y + 1), "  [", fill=Values.white, font=Values.minecraft_16)

    startpoint += draw.textlength("  [", font=Values.minecraft_16)

    # Filled in squared for bar
    squares = "■" * int(progress_out_of_10)

    draw.text((startpoint + 2, position_y - 6), squares, fill=Values.black, font=Values.arial_24)
    draw.text((startpoint, position_y - 8), squares, fill=Values.aqua, font=Values.arial_24)

    startpoint += draw.textlength(squares, font=Values.arial_24)

    # Blank in squared for bar
    squares = "■" * (10 - int(progress_out_of_10))

    draw.text((startpoint + 2, position_y - 6), squares, fill=Values.black, font=Values.arial_24)
    draw.text((startpoint, position_y - 8), squares, fill=Values.gray, font=Values.arial_24)

    startpoint += draw.textlength(squares, font=Values.arial_24) + 3

    # Right bracket for bar
    draw.text((startpoint + 2, position_y + 3), "] ", fill=Values.black, font=Values.minecraft_16)
    draw.text((startpoint, position_y + 1), "] ", fill=Values.white, font=Values.minecraft_16)

    startpoint += draw.textlength("] ", font=Values.minecraft_16)

    # Second value (next level)
    render_level(
        level=level+1,
        font_size=20, 
        image=image,
        position=(startpoint, position_y)
    )


def render_progress_text(box_positions: tuple, position_y: int, progress: int, target: int, draw: ImageDraw):
    """
    :param box_positions: Values for container to center the text (box_width, box_start_x)
    :param position_y: Y position to render the text
    :param progress: The progress made on the current level
    :param target: The max progress for the current level
    :param draw: The ImageDraw object used to draw on the image
    """

    # Progress text (Progress: value / target)
    totallength = draw.textlength(f'Progress: {progress} / {target}', font=Values.minecraft_20)
    startpoint = int((box_positions[0] - totallength) / 2) + box_positions[1]

    draw.text((startpoint + 2, position_y + 2), 'Progress: ', fill=Values.black, font=Values.minecraft_20)
    draw.text((startpoint, position_y), 'Progress: ', fill=Values.white, font=Values.minecraft_20)

    startpoint += draw.textlength('Progress: ', font=Values.minecraft_20)

    draw.text((startpoint + 2, position_y + 2), progress, fill=Values.black, font=Values.minecraft_20)
    draw.text((startpoint, position_y), progress, fill=Values.light_purple, font=Values.minecraft_20)

    startpoint += draw.textlength(progress, font=Values.minecraft_20)

    draw.text((startpoint + 2, position_y + 2), ' / ', fill=Values.black, font=Values.minecraft_20)
    draw.text((startpoint, position_y), ' / ', fill=Values.white, font=Values.minecraft_20)

    startpoint += draw.textlength(' / ', font=Values.minecraft_20)

    draw.text((startpoint + 2, position_y + 2), target, fill=Values.black, font=Values.minecraft_20)
    draw.text((startpoint, position_y), target, fill=Values.green, font=Values.minecraft_20)
