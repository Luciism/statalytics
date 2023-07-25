from PIL import Image, ImageDraw, ImageFont

from calc.total import Stats
from statalib import to_thread
from statalib.render import (
    render_display_name,
    get_background,
    paste_skin,
    render_progress_bar,
    render_progress_text
)


@to_thread
def render_total(name, uuid, mode, hypixel_data, skin_res, save_dir, method):
    stats = Stats(name, mode, hypixel_data)
    level = stats.level
    rank_info = stats.rank_info

    progress, target, progress_of_10 = stats.progress
    loot_chests, coins = stats.get_chest_and_coins()
    most_played = stats.most_played

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


    image = get_background(path='./assets/bg/total', uuid=uuid,
                           default='base', level=level, rank_info=rank_info)

    image = image.convert("RGBA")

    draw = ImageDraw.Draw(image)
    minecraft_16 = ImageFont.truetype('./assets/fonts/minecraft.ttf', 16)

    def leng(text, width):
        return (width - draw.textlength(text, font=minecraft_16)) / 2

    green = (85, 255, 85)
    white = (255, 255, 255)
    red = (255, 76, 76)
    black = (0, 0, 0)
    gold = (255, 170, 0)
    light_purple = (255, 85, 255)

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
    render_display_name(
        username=name,
        rank_info=rank_info,
        image=image,
        font_size=22,
        position=(226, 31),
        align='center'
    )

    render_progress_bar(
        level=level,
        progress_of_10=progress_of_10,
        position=(226, 91),
        image=image,
        align='center'
    )

    render_progress_text(
        progress=progress,
        target=target,
        position=(226, 122),
        image=image,
        align='center'
    )

    image = paste_skin(skin_res, image, positions=(466, 69))

    # Paste overlay
    overlay_image = Image.open(f'./assets/bg/total/overlay_{method}.png')
    overlay_image = overlay_image.convert("RGBA")
    image.paste(overlay_image, (0, 0), overlay_image)

    # Save the image
    image.save(f'./database/rendered/{save_dir}/{mode.lower()}.png')
