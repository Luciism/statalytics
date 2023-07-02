from PIL import Image, ImageDraw, ImageFont

from calc.resources import Resources
from helper.rendername import get_rank_prefix, render_rank
from helper.rendertools import get_background
from helper.renderprogress import render_progress_text, render_progress_bar

def render_resources(name, uuid, mode, hypixel_data, save_dir):
    resources = Resources(name, mode, hypixel_data)
    level = resources.level
    player_rank_info = resources.player_rank_info
    progress, target, progress_out_of_10 = resources.progress
    total_collected = f'{resources.total_resources:,}'

    iron_collected = f'{resources.iron_collected:,}'
    gold_collected = f'{resources.gold_collected:,}'
    diamonds_collected = f'{resources.diamonds_collected:,}'
    emeralds_collected = f'{resources.emeralds_collected:,}'

    iron_per_game, gold_per_game, diamonds_per_game, emeralds_per_game = resources.get_per_game()
    iron_per_star, gold_per_star, diamonds_per_star, emeralds_per_star = resources.get_per_star()
    iron_percentage, gold_percentage, diamond_percentage, emerald_percentage = resources.get_percentages()
    iron_most_mode, gold_most_mode, diamond_most_mode, emerald_most_mode = resources.get_most_modes()

    image = get_background(path='./assets/bg/resources', uuid=uuid,
                           default='base', level=level, rank_info=player_rank_info)

    image = image.convert("RGBA")

    draw = ImageDraw.Draw(image)
    minecraft_16 = ImageFont.truetype('./assets/minecraft.ttf', 16)
    minecraft_22 = ImageFont.truetype('./assets/minecraft.ttf', 22)

    def leng(text, container_width):
        """Returns startpoint for centering text in a box"""
        return (container_width - draw.textlength(text, font=minecraft_16)) / 2

    green = (85, 255, 85)
    white = (255, 255, 255)
    black = (0, 0, 0)
    gold = (255, 170, 0)
    aqua = (85, 255, 255)
    light_purple = (255, 85, 255)

    data = (
        ((leng(iron_collected, 141)+19, 189), iron_collected, white),
        ((leng(gold_collected, 141)+174, 189), gold_collected, gold),
        ((leng(diamonds_collected, 141)+329, 189), diamonds_collected, aqua),
        ((leng(emeralds_collected, 141)+483, 189), emeralds_collected, green),
        
        ((leng(iron_per_game, 141)+19, 249), iron_per_game, white),
        ((leng(gold_per_game, 141)+174, 249), gold_per_game, gold),
        ((leng(diamonds_per_game, 141)+329, 249), diamonds_per_game, aqua),
        ((leng(emeralds_per_game, 141)+483, 249), emeralds_per_game, green),
        
        ((leng(iron_per_star, 141)+19, 309), iron_per_star, white),
        ((leng(gold_per_star, 141)+174, 309), gold_per_star, gold),
        ((leng(diamonds_per_star, 141)+329, 309), diamonds_per_star, aqua),
        ((leng(emeralds_per_star, 141)+483, 309), emeralds_per_star, green),
        
        ((leng(iron_percentage, 141)+19, 369), iron_percentage, white),
        ((leng(gold_percentage, 141)+174, 369), gold_percentage, gold),
        ((leng(diamond_percentage, 141)+329, 369), diamond_percentage, aqua),
        ((leng(emerald_percentage, 141)+483, 369), emerald_percentage, green),
        
        ((leng(iron_most_mode, 141)+19, 429), iron_most_mode, white),
        ((leng(gold_most_mode, 141)+174, 429), gold_most_mode, gold),
        ((leng(diamond_most_mode, 141)+329, 429), diamond_most_mode, aqua),
        ((leng(emerald_most_mode, 141)+483, 429), emerald_most_mode, green),

        ((leng(total_collected, 174)+450, 129), total_collected, light_purple),
    )

    for values in data:
        start_x, start_y = values[0]
        stat = values[1]

        draw.text((start_x + 2, start_y + 2), stat, fill=black, font=minecraft_16)
        draw.text((start_x, start_y), stat, fill=values[2], font=minecraft_16)

    # Unloopable stuff
    rank_prefix = get_rank_prefix(player_rank_info)
    totallength = draw.textlength(f'{rank_prefix}{name}', font=minecraft_22)
    player_x = round((415 - totallength) / 2) + 19
    render_rank(name, position_x=player_x, position_y=27, rank_prefix=rank_prefix,
                player_rank_info=player_rank_info, draw=draw, fontsize=22)


    # Render the level progress
    render_progress_bar(box_positions=(415, 19), position_y=88, level=level,
                        progress_out_of_10=progress_out_of_10, image=image)

    render_progress_text(box_positions=(415, 19), position_y=119,
                         progress=progress, target=target, draw=draw)

    # Render Mode
    draw.text((leng(f'({mode})', 174)+451, 66), f'({mode})', fill=black, font=minecraft_16)
    draw.text((leng(f'({mode})', 174)+450, 65), f'({mode})', fill=white, font=minecraft_16)

    # Paste overlay
    overlay_image = Image.open(f'./assets/bg/resources/overlay.png')
    overlay_image = overlay_image.convert("RGBA")
    image.paste(overlay_image, (0, 0), overlay_image)

    # Save the image
    image.save(f'./database/activerenders/{save_dir}/{mode.lower()}.png')
