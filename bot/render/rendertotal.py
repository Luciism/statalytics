import os
from io import BytesIO
from PIL import Image, ImageDraw, ImageFont
from calc.calctotal import Stats
from helper.rendername import render_name_rank_only, render_level
from helper.custombackground import background

def rendertotal(name, uuid, mode, hypixel_data, skin_res, save_dir, method):
    # Open the image
    image_location = background(path=f'{os.getcwd()}/assets/total', uuid=uuid, default='base')
    image = Image.open(image_location)
    image = image.convert("RGBA")

    # Create an ImageDraw object
    draw = ImageDraw.Draw(image)

    # Choose a font and font size
    minecraft_13 = ImageFont.truetype(f'{os.getcwd()}/assets/minecraft.ttf', 13)
    minecraft_16 = ImageFont.truetype(f'{os.getcwd()}/assets/minecraft.ttf', 16)
    minecraft_20 = ImageFont.truetype(f'{os.getcwd()}/assets/minecraft.ttf', 20)
    arial_24 = ImageFont.truetype(f"{os.getcwd()}/assets/arial.ttf", 24)

    # Define the text colors
    green = (85, 255, 85)
    white = (255, 255, 255)
    red = (255, 76, 76)
    black = (0, 0, 0)
    gold = (255, 170, 0)
    light_purple = (255, 85, 255)
    gray = (170, 170, 170)
    aqua = (85, 255, 255)

    stats = Stats(name, uuid, mode, hypixel_data)
    level = stats.level
    playerrank = stats.get_player_rank()

    progress, target, progress_out_of_10 = stats.get_progress()
    loot_chests, coins = stats.get_chest_and_coins()
    most_played = stats.get_most_played()

    if method == "generic":
        wins, losses, wlr = stats.get_wins()
        final_kills, final_deaths, fkdr = stats.get_finals()
        beds_broken, beds_lost, bblr = stats.get_beds()
        kills, deaths, kdr = stats.get_kills()
        games_played, times_voided, items_purchased, winstreak = stats.get_misc()
    else:
        wins, losses, wlr = stats.get_falling_kills()
        final_kills, final_deaths, fkdr = stats.get_void_kills()
        beds_broken, beds_lost, bblr = stats.get_ranged_kills()
        kills, deaths, kdr = stats.get_fire_kills()
        games_played, times_voided, items_purchased, winstreak = stats.get_misc_pointless()

    def leng(text, width):
        return (width - draw.textlength(text, font=ImageFont.truetype(f'{os.getcwd()}/assets/minecraft.ttf', 16))) / 2

    data = (
        ((leng(wins, 140) + 17, 190), (wins, green)),
        ((leng(losses, 140) + 171, 190), (losses, red)),
        ((leng(wlr, 107) + 325, 190), (wlr, gold)),
        ((leng(final_kills, 140) + 17, 249), (final_kills, green)),
        ((leng(final_deaths, 140) + 171, 249), (final_deaths, red)),
        ((leng(fkdr, 107) + 325, 249), (fkdr, gold)),
        ((leng(beds_broken, 140) + 17, 308), (beds_broken, green)),
        ((leng(beds_lost, 140) + 171, 308), (beds_lost, red)),
        ((leng(bblr, 107) + 325, 308), (bblr, gold)),
        ((leng(kills, 140) + 17, 367), (kills, green)),
        ((leng(deaths, 140) + 171, 367), (deaths, red)),
        ((leng(kdr, 107) + 325, 367), (kdr, gold)),
        ((leng(winstreak, 130) + 17, 427), (winstreak, light_purple)),
        ((leng(loot_chests, 127) + 163, 427), (loot_chests, light_purple)),
        ((leng(coins, 128) + 306, 427), (coins, light_purple)),
        ((leng(games_played, 171) + 452, 249), (games_played, light_purple)),
        ((leng(most_played, 171) + 452, 308), (most_played, light_purple)),
        ((leng(times_voided, 171) + 452, 367), (times_voided, light_purple)),
        ((leng(items_purchased, 171) + 452, 427), (items_purchased, light_purple)),
        ((leng(f'({mode.title()})', 171) + 452, 46), (f'({mode.title()})', white)),
    )

    for values in data:
        start_x, start_y = values[0]
        stat = values[1][0]

        draw.text((start_x + 2, start_y + 2), stat, fill=black, font=minecraft_16)
        draw.text((start_x, start_y), stat, fill=values[1][1], font=minecraft_16)

    # Render the player name
    render_name_rank_only(name, playerrank, image, box_x=19, box_width=415, player_y=31, fontsize=22)

    # Render the progress
    totallength = draw.textlength(f'[{level}][{level + 1}]', font=minecraft_20) + draw.textlength(' [] ', font=minecraft_13) + draw.textlength('■■■■■■■■■■', font=arial_24) + 32 # 32 for width of pasted star symbol
    startpoint = int((415 - totallength) / 2) + 19
    progress_bar_y = 91

    # First value (current level)
    render_level(level, image, startpoint, progress_bar_y, 20)

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
    render_level(level + 1, image, startpoint, progress_bar_y, 20)

    # Progress text (Progress: value / target)
    totallength = draw.textlength(f'Progress: {progress} / {target}', font=minecraft_20)
    startpoint = int((415 - totallength) / 2) + 19
    progress_y = 122

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

    # Render Skin
    skin = Image.open(BytesIO(skin_res))
    image.paste(skin, (466, 69), skin)

    # Paste overlay
    overlay_image = Image.open(f'{os.getcwd()}/assets/total/overlay_{method}.png')
    overlay_image = overlay_image.convert("RGBA")
    image.paste(overlay_image, (0, 0), overlay_image)

    # Save the image
    image.save(f'{os.getcwd()}/database/activerenders/{save_dir}/{mode.lower()}.png')
