from datetime import datetime

from PIL import Image, ImageDraw, ImageFont

from calc.year import YearStats
from statalib import to_thread
from statalib.render import (
    get_background,
    paste_skin,
    box_center_text,
    render_level,
    render_rank,
    get_rank_prefix
)


@to_thread
def render_year(name, uuid, session, year, mode,
                hypixel_data, skin_res, save_dir):
    stats = YearStats(name, uuid, session, year, mode, hypixel_data)
    level = int(stats.level_hypixel)
    target = stats.get_target()
    rank_info = stats.rank_info
    days_to_go = str(stats.days_to_go)
    stars_per_day = f'{round(stats.stars_per_day, 2):,}'
    items_purchased = stats.get_items_purchased()

    years_to_go = year - datetime.now().year
    complete_percent = f'{round(((365 * years_to_go) - int(days_to_go)) / (365 * years_to_go) * 100, 2)}%'

    kills, deaths, kdr = stats.get_kills()
    final_kills, final_deaths, fkdr = stats.get_finals()
    beds_broken, beds_lost, bblr = stats.get_beds()
    wins, losses, wlr = stats.get_wins()
    wins_per_star, finals_per_star, beds_per_star = stats.get_per_star()
    year = str(year)

    image = get_background(path='./assets/bg/year', uuid=uuid,
                           default='base', level=level, rank_info=rank_info)

    image = image.convert("RGBA")

    draw = ImageDraw.Draw(image)
    minecraft_16 = ImageFont.truetype('./assets/minecraft.ttf', 16)
    minecraft_18 = ImageFont.truetype('./assets/minecraft.ttf', 18)
    minecraft_20 = ImageFont.truetype('./assets/minecraft.ttf', 20)
    minecraft_22 = ImageFont.truetype('./assets/minecraft.ttf', 22)

    def leng(text, width):
        return (width - draw.textlength(text, font=minecraft_16)) / 2

    green = (85, 255, 85)
    white = (255, 255, 255)
    red = (255, 76, 76)
    black = (0, 0, 0)
    gold = (255, 170, 0)
    light_purple = (255, 85, 255)

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
        ((leng(complete_percent, 171) + 452, 250), (complete_percent, light_purple)),
        ((leng(days_to_go, 171) + 452, 309), (days_to_go, light_purple)),
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
    render_rank(name, rank_info, draw, fontsize=22, pos_y=28, center_x=(415, 19))

    # Projection Date
    year_txt = "Predictions For Year: "

    total_width = draw.textlength(f"{year_txt}{year}", font=minecraft_18)
    year_x = ((417 - total_width) / 2) + 21
    year_y = 425

    draw.text((year_x + 2, year_y + 2), year_txt, fill=black, font=minecraft_18)
    draw.text((year_x, year_y), year_txt, fill=white, font=minecraft_18)

    year_x += draw.textlength(year_txt, font=minecraft_18)

    draw.text((year_x + 2, year_y + 2), year, fill=black, font=minecraft_18)
    draw.text((year_x, year_y), year, fill=light_purple, font=minecraft_18)

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

    box_center_text(f'Year {year}', draw, box_width=171,
                    box_start=452, text_y=27, font=minecraft_18)

    # Paste Skin
    image = paste_skin(skin_res, image, positions=(466, 69))

    # Paste overlay
    overlay_image = Image.open('./assets/bg/year/overlay.png')
    overlay_image = overlay_image.convert('RGBA')
    image.paste(overlay_image, (0, 0), overlay_image)

    # Save the image
    image.save(f'./database/rendered/{save_dir}/{mode.lower()}.png')
    if mode.lower() == "overall":
        return level
