from io import BytesIO

from PIL import Image, ImageDraw, ImageFont
from calc.calcresources import Resources
from helper.rendername import render_level, get_rank_prefix, render_rank
from helper.custombackground import background

def renderresources(name, uuid, mode, hypixel_data, save_dir):
    # Open the image
    image_location = background(path='./assets/resources', uuid=uuid, default='base')
    image = Image.open(image_location)
    image = image.convert("RGBA")

    # Create an ImageDraw object
    draw = ImageDraw.Draw(image)

    # Choose a font and font size
    minecraft_13 = ImageFont.truetype('./assets/minecraft.ttf', 13)
    minecraft_16 = ImageFont.truetype('./assets/minecraft.ttf', 16)
    minecraft_20 = ImageFont.truetype('./assets/minecraft.ttf', 20)
    minecraft_22 = ImageFont.truetype('./assets/minecraft.ttf', 22)
    arial_24 = ImageFont.truetype(f"./assets/arial.ttf", 24)

    # Define the text colors
    green = (85, 255, 85)
    white = (255, 255, 255)
    black = (0, 0, 0)
    gray = (170, 170, 170)
    gold = (255, 170, 0)
    aqua = (85, 255, 255)
    light_purple = (255, 85, 255)

    # Define the values
    resources = Resources(name, mode, hypixel_data)
    level = resources.level
    player_rank_info = resources.get_player_rank_info()

    progress, target, progress_out_of_10 = resources.get_progress()

    iron_collected = f'{resources.iron_collected:,}'
    gold_collected = f'{resources.gold_collected:,}'
    diamonds_collected = f'{resources.diamonds_collected:,}'
    emeralds_collected = f'{resources.emeralds_collected:,}'

    iron_per_game, gold_per_game, diamonds_per_game, emeralds_per_game = resources.get_per_game()
    iron_per_star, gold_per_star, diamonds_per_star, emeralds_per_star = resources.get_per_star()
    iron_percentage, gold_percentage, diamond_percentage, emerald_percentage = resources.get_percentages()
    iron_most_mode, gold_most_mode, diamond_most_mode, emerald_most_mode = resources.get_most_modes()

    total_collected = f'{resources.total_resources:,}'

    def leng(text, container_width):
        """Returns startpoint for centering text in a box"""
        return (container_width - draw.textlength(text, font=ImageFont.truetype('./assets/minecraft.ttf', 16))) / 2

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
    render_rank(name, position_x=player_x, position_y=27, rank_prefix=rank_prefix, player_rank_info=player_rank_info, draw=draw, fontsize=22)


    # ------ Render the progress ------ #
    totallength = draw.textlength(f'[{level}][{level + 1}]', font=minecraft_20) + draw.textlength(' [] ', font=minecraft_13) + draw.textlength('■■■■■■■■■■', font=arial_24) + 32 # 32 for width of pasted star symbol
    startpoint = int((415 - totallength) / 2) + 19
    progress_bar_y = 88

    # First value (current level)
    render_level(level, position_x=startpoint, position_y=progress_bar_y, fontsize=20, image=image)

    startpoint += draw.textlength(f'[{level}]', font=minecraft_20) + 16

    # Left bracket for bar
    draw.text((startpoint + 2, progress_bar_y + 3), " [", fill=black, font=minecraft_16)
    draw.text((startpoint, progress_bar_y + 1), " [", fill=white, font=minecraft_16)

    startpoint += draw.textlength(" [", font=minecraft_16)

    # Filled in squared for bar
    squares = "■" * int(progress_out_of_10)

    draw.text((startpoint + 2, progress_bar_y - 6), squares, fill=black, font=arial_24)
    draw.text((startpoint, progress_bar_y - 8), squares, fill=aqua, font=arial_24)

    startpoint += draw.textlength(squares, font=arial_24)

    # Blank in squared for bar
    squares = "■" * (10 - int(progress_out_of_10))

    draw.text((startpoint + 2, progress_bar_y - 6), squares, fill=black, font=arial_24)
    draw.text((startpoint, progress_bar_y - 8), squares, fill=gray, font=arial_24)

    startpoint += draw.textlength(squares, font=arial_24) + 3

    # Right bracket for bar
    draw.text((startpoint + 2, progress_bar_y + 3), "] ", fill=black, font=minecraft_16)
    draw.text((startpoint, progress_bar_y + 1), "] ", fill=white, font=minecraft_16)

    startpoint += draw.textlength("] ", font=minecraft_16)

    # Second value (next level)
    render_level(level+1, position_x=startpoint, position_y=progress_bar_y, fontsize=20, image=image)

    # Progress text (Progress: value / target)
    totallength = draw.textlength(f'Progress: {progress} / {target}', font=minecraft_20)
    startpoint = int((415 - totallength) / 2) + 19
    progress_y = 119

    draw.text((startpoint + 2, progress_y + 2), 'Progress: ', fill=black, font=minecraft_20)
    draw.text((startpoint, progress_y), 'Progress: ', fill=white, font=minecraft_20)

    startpoint += draw.textlength('Progress: ', font=minecraft_20)

    draw.text((startpoint + 2, progress_y + 2), progress, fill=black, font=minecraft_20)
    draw.text((startpoint, progress_y), progress, fill=light_purple, font=minecraft_20)

    startpoint += draw.textlength(progress, font=minecraft_20)

    draw.text((startpoint + 2, progress_y + 2), ' / ', fill=black, font=minecraft_20)
    draw.text((startpoint, progress_y), ' / ', fill=white, font=minecraft_20)

    startpoint += draw.textlength(' / ', font=minecraft_20)

    draw.text((startpoint + 2, progress_y + 2), target, fill=black, font=minecraft_20)
    draw.text((startpoint, progress_y), target, fill=green, font=minecraft_20)

    # Render Mode
    draw.text((leng(f'({mode})', 174)+451, 66), f'({mode})', fill=black, font=minecraft_16)
    draw.text((leng(f'({mode})', 174)+450, 65), f'({mode})', fill=white, font=minecraft_16)

    # Paste overlay
    overlay_image = Image.open(f'./assets/resources/overlay.png')
    overlay_image = overlay_image.convert("RGBA")
    image.paste(overlay_image, (0, 0), overlay_image)

    # Save the image
    image.save(f'./database/activerenders/{save_dir}/{mode.lower()}.png')
