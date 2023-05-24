from PIL import Image, ImageDraw, ImageFont
from calc.projection import ProjectedStats
from helper.custombackground import background
from helper.rendername import render_level, render_rank, get_rank_prefix, paste_skin

def render_projection(name, uuid, session, mode, target, hypixel_data, skin_res, save_dir):
    image_location = background(path='./assets/projection', uuid=uuid, default='base')
    image = Image.open(image_location)
    image = image.convert("RGBA")

    draw = ImageDraw.Draw(image)

    minecraft_16 = ImageFont.truetype('./assets/minecraft.ttf', 16)
    minecraft_18 = ImageFont.truetype('./assets/minecraft.ttf', 18)
    minecraft_20 = ImageFont.truetype('./assets/minecraft.ttf', 20)
    minecraft_22 = ImageFont.truetype('./assets/minecraft.ttf', 22)

    green = (85, 255, 85)
    white = (255, 255, 255)
    red = (255, 76, 76)
    black = (0, 0, 0)
    gold = (255, 170, 0)
    light_purple = (255, 85, 255)

    stats = ProjectedStats(name, uuid, session, mode, target, hypixel_data)
    level = int(stats.level_hypixel)
    player_rank_info = stats.player_rank_info
    projection_date = stats.get_projection_date()
    stars_per_day = stats.get_stars_per_day()
    items_purchased = stats.get_items_purchased()
    stars_to_go = stats.stars_to_go

    kills, deaths, kdr = stats.get_kills()
    final_kills, final_deaths, fkdr = stats.get_finals()
    beds_broken, beds_lost, bblr = stats.get_beds()
    wins, losses, wlr = stats.get_wins()
    wins_per_star, finals_per_star, beds_per_star = stats.get_per_star()

    def leng(text, width):
        return (width - draw.textlength(text, font=ImageFont.truetype('./assets/minecraft.ttf', 16))) / 2

    data = (
        ((leng(wins, 140) + 21, 148), (wins, green)),
        ((leng(losses, 140) + 175, 148), (losses, red)),
        ((leng(wlr, 107) + 329, 148), (wlr, gold)),
        ((leng(final_kills, 140) + 21, 207), (final_kills, green)),
        ((leng(final_deaths, 140) + 175, 207), (final_deaths, red)),
        ((leng(fkdr, 107) + 329, 207), (fkdr, gold)),
        ((leng(beds_broken, 140) + 21, 266), (beds_broken, green)),
        ((leng(beds_lost, 140) + 175, 266), (beds_lost, red)),
        ((leng(bblr, 107) + 329, 266), (bblr, gold)),
        ((leng(kills, 140) + 21, 325), (kills, green)),
        ((leng(deaths, 140) + 175, 325), (deaths, red)),
        ((leng(kdr, 107) + 329, 325), (kdr, gold)),
        ((leng(wins_per_star, 128) + 23, 385), (wins_per_star, light_purple)),
        ((leng(finals_per_star, 127) + 167, 385), (finals_per_star, light_purple)),
        ((leng(beds_per_star, 128) + 310, 385), (beds_per_star, light_purple)),
        ((leng(stats.complete_percent, 171) + 452, 250), (stats.complete_percent, light_purple)),
        ((leng(stars_to_go, 171) + 452, 309), (stars_to_go, light_purple)),
        ((leng(stars_per_day, 171) + 452, 368), (stars_per_day, light_purple)),
        ((leng(items_purchased, 171) + 452, 427), (items_purchased, light_purple)),
        ((leng(f'({mode.title()})', 171) + 452, 46), (f'({mode.title()})', white)),
    )

    for values in data:
        start_x, start_y = values[0]
        stat = values[1][0]

        draw.text((start_x + 2, start_y + 2), stat, fill=black, font=minecraft_16)
        draw.text((start_x, start_y), stat, fill=values[1][1], font=minecraft_16)

    # Render name
    rank_prefix = get_rank_prefix(player_rank_info)
    totallength = draw.textlength(f'{rank_prefix}{name}', font=minecraft_22)
    player_x = round((415 - totallength) / 2) + 19

    render_rank(name, player_x, position_y=28, rank_prefix=rank_prefix, player_rank_info=player_rank_info, draw=draw, fontsize=22)

    # Projection Date
    projection_date_txt = "Projected to hit on: "

    total_width = draw.textlength(f"{projection_date_txt}{projection_date}", font=minecraft_18)
    projection_date_x = ((417 - total_width) / 2) + 21
    projection_date_y = 425

    draw.text((projection_date_x + 2, projection_date_y + 2), projection_date_txt, fill=black, font=minecraft_18)
    draw.text((projection_date_x, projection_date_y), projection_date_txt, fill=white, font=minecraft_18)

    projection_date_x += draw.textlength(projection_date_txt, font=minecraft_18)

    draw.text((projection_date_x + 2, projection_date_y + 2), projection_date, fill=black, font=minecraft_18)
    draw.text((projection_date_x, projection_date_y), projection_date, fill=light_purple, font=minecraft_18)

    # Render Progress
    total_width = draw.textlength(f"[{level}]  / [{target}]", font=minecraft_20) + 32 # 32 for pasted star width
    progress_x = ((415 - total_width) / 2) + 19
    progress_y = 84

    render_level(level, progress_x, progress_y, 20, image)

    progress_x += draw.textlength(f"[{level}]", font=minecraft_20) + 16

    draw.text((progress_x + 2, progress_y + 2), "  / ", fill=black, font=minecraft_18)
    draw.text((progress_x, progress_y), "  / ", fill=white, font=minecraft_18)

    progress_x += draw.textlength("  / ", font=minecraft_20)

    render_level(target, progress_x, progress_y, 20, image)

    paste_skin(skin_res, image, positions=(466, 69))

    # Paste overlay
    overlay_image = Image.open('./assets/projection/overlay.png')
    image.paste(overlay_image, (0, 0), overlay_image)

    # Save the image
    image.save(f'./database/activerenders/{save_dir}/{mode.lower()}.png')
    if mode.lower() == "overall":
        return level
