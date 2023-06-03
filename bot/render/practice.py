from io import BytesIO

from PIL import Image, ImageDraw, ImageFont

from calc.practice import Practice
from helper.rendername import render_rank, get_rank_prefix
from helper.rendertools import get_background, paste_skin
from helper.renderprogress import render_progress_bar


def render_practice(name, uuid, hypixel_data, skin_res):
    practice = Practice(name, hypixel_data)
    level = practice.level
    player_rank_info = practice.player_rank_info
    progress_out_of_10 = practice.progress[2]

    bridging_completed, bridging_failed, bridging_ratio = practice.get_bridging_stats()
    pearl_completed, pearl_failed, pearl_ratio = practice.get_pearl_stats()
    tnt_completed, tnt_failed, tnt_ratio = practice.get_tnt_stats()
    mlg_completed, mlg_failed, mlg_ratio = practice.get_mlg_stats()
    straight_short, straight_medium, straight_long, straight_average = practice.get_straight_times()
    diagonal_short, diagonal_medium, diagonal_long, diagonal_average = practice.get_diagonal_times()
    blocks_placed = practice.get_blocks_placed()

    attempts = sum((int(value.replace(',', '')) for value in (bridging_completed, bridging_failed,
        tnt_completed, tnt_failed, mlg_completed, mlg_failed, pearl_completed, pearl_failed)))
    attempts = f'{attempts:,}'

    image = get_background(path='./assets/practice', uuid=uuid, default='base', level=level, rank_info=player_rank_info)
    image = image.convert("RGBA")

    draw = ImageDraw.Draw(image)
    minecraft_16 = ImageFont.truetype('./assets/minecraft.ttf', 16)
    minecraft_22 = ImageFont.truetype('./assets/minecraft.ttf', 22)


    def leng(text, width):
        return (width - draw.textlength(text, font=minecraft_16)) / 2

    white = (255, 255, 255)
    green = (85, 255, 85)
    black = (0, 0, 0)
    gold = (255, 170, 0)
    red = (255, 85, 85)
    light_purple = (255, 85, 255)

    data = (
        ((leng(bridging_completed, 140) + 17, 131), bridging_completed, green),
        ((leng(bridging_failed, 140) + 171, 131), bridging_failed, red),
        ((leng(bridging_ratio, 107) + 325, 131), bridging_ratio, gold),
        ((leng(tnt_completed, 140) + 17, 190), tnt_completed, green),
        ((leng(tnt_failed, 140) + 171, 190), tnt_failed, red),
        ((leng(tnt_ratio, 107) + 325, 190), tnt_ratio, gold),
        ((leng(mlg_completed, 140) + 17, 249), mlg_completed, green),
        ((leng(mlg_failed, 140) + 171, 249), mlg_failed, red),
        ((leng(mlg_ratio, 107) + 325, 249), mlg_ratio, gold),
        ((leng(pearl_completed, 140) + 17, 308), pearl_completed, green),
        ((leng(pearl_failed, 140) + 171, 308), pearl_failed, red),
        ((leng(pearl_ratio, 107) + 325, 308), pearl_ratio, gold),
        ((leng(straight_short, 142) + 17, 368), straight_short, light_purple),
        ((leng(straight_medium, 139) + 173, 368), straight_medium, light_purple),
        ((leng(straight_long, 141) + 327, 368), straight_long, light_purple),
        ((leng(straight_average, 140) + 483, 368), straight_average, light_purple),
        ((leng(diagonal_short, 142) + 17, 426), diagonal_short, light_purple),
        ((leng(diagonal_medium, 139) + 173, 426), diagonal_medium, light_purple),
        ((leng(diagonal_long, 141) + 327, 426), diagonal_long, light_purple),
        ((leng(diagonal_average, 140) + 483, 426), diagonal_average, light_purple),
        ((leng(attempts, 171) + 452, 249), attempts, light_purple),
        ((leng(blocks_placed, 171) + 452, 308), blocks_placed, light_purple),
        ((leng('(Overall)', 171) + 452, 46), '(Overall)', white),
    )

    for values in data:
        start_x, start_y = values[0]
        stat = values[1]
        draw.text((start_x + 2, start_y + 2), stat, fill=black, font=minecraft_16)
        draw.text((start_x, start_y), stat, fill=values[2], font=minecraft_16)

    # Render name & progress bar
    rank_prefix = get_rank_prefix(player_rank_info)
    totallength = draw.textlength(f'{rank_prefix}{name}', font=minecraft_22)
    player_x = round((415 - totallength) / 2) + 19

    render_rank(name, position_x=player_x, position_y=30, rank_prefix=rank_prefix,
                player_rank_info=player_rank_info, draw=draw, fontsize=22)

    render_progress_bar(box_positions=(415, 19), position_y=61, level=level,
                        progress_out_of_10=progress_out_of_10, image=image)

    image = paste_skin(skin_res, image, positions=(466, 69))

    # Paste overlay
    overlay_image = Image.open(f'./assets/practice/overlay.png')
    overlay_image = overlay_image.convert("RGBA")
    image.paste(overlay_image, (0, 0), overlay_image)

    # Return the image
    image_bytes = BytesIO()
    image.save(image_bytes, format='PNG')
    image_bytes.seek(0)

    return image_bytes
