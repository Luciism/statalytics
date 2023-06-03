from PIL import Image, ImageDraw, ImageFont

from calc.session import SessionStats
from helper.rendername import render_rank, get_rank_prefix
from helper.rendertools import get_background, paste_skin
from helper.renderprogress import render_progress_bar


def render_session(name, uuid, session, mode, hypixel_data, skin_res, save_dir):
    stats = SessionStats(name, uuid, session, mode, hypixel_data)

    progress_out_of_10 = stats.progress[2]
    total_sessions = stats.total_sessions

    player_rank_info = stats.player_rank_info
    most_played = stats.get_most_played()
    level = stats.level
    date_started = stats.date_started

    wins, losses, wlr = stats.get_wins()
    final_kills, final_deaths, fkdr = stats.get_finals()
    beds_broken, beds_lost, bblr = stats.get_beds()
    kills, deaths, kdr = stats.get_kills()
    wins_per_day, finals_per_day, beds_per_day, stars_per_day = stats.get_per_day()

    image = get_background(path='./assets/session', uuid=uuid,
                           default='base', level=level, rank_info=player_rank_info)

    image = image.convert("RGBA")

    draw = ImageDraw.Draw(image)
    minecraft_16 = ImageFont.truetype('./assets/minecraft.ttf', 16)
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
        ((leng(wins, 140) + 17, 131), (wins, green)),
        ((leng(losses, 140) + 171, 131), (losses, red)),
        ((leng(wlr, 107) + 325, 131), (wlr, gold)),

        ((leng(final_kills, 140) + 17, 190), (final_kills, green)),
        ((leng(final_deaths, 140) + 171, 190), (final_deaths, red)),
        ((leng(fkdr, 107) + 325, 190), (fkdr, gold)),

        ((leng(beds_broken, 140) + 17, 249), (beds_broken, green)),
        ((leng(beds_lost, 140) + 171, 249), (beds_lost, red)),
        ((leng(bblr, 107) + 325, 249), (bblr, gold)),

        ((leng(kills, 140) + 17, 308), (kills, green)),
        ((leng(deaths, 140) + 171, 308), (deaths, red)),
        ((leng(kdr, 107) + 325, 308), (kdr, gold)),

        ((leng(stars_per_day, 130) + 17, 368), (stars_per_day, light_purple)),
        ((leng(stats.stars_gained, 127) + 163, 368), (stats.stars_gained, light_purple)),
        ((leng(stats.games_played, 128) + 306, 368), (stats.games_played, light_purple)),

        ((leng(wins_per_day, 130) + 17, 427), (wins_per_day, light_purple)),
        ((leng(finals_per_day, 127) + 163, 427), (finals_per_day, light_purple)),
        ((leng(beds_per_day, 128) + 306, 427), (beds_per_day, light_purple)),

        ((leng(f"# {session}", 171) + 452, 249), (f"# {session}", light_purple)),
        ((leng(total_sessions, 171) + 452, 308), (total_sessions, light_purple)),
        ((leng(date_started, 171) + 452, 367), (date_started, light_purple)),
        ((leng(most_played, 171) + 452, 427), (most_played, light_purple)),
        ((leng(f'({mode.title()})', 171) + 452, 46), (f'({mode.title()})', white)),
    )

    for values in data:
        start_x, start_y = values[0]
        stat = values[1][0]

        draw.text((start_x + 2, start_y + 2), stat, fill=black, font=minecraft_16)
        draw.text((start_x, start_y), stat, fill=values[1][1], font=minecraft_16)

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
    overlay_image = Image.open(f'./assets/session/overlay.png')
    overlay_image = overlay_image.convert("RGBA")
    image.paste(overlay_image, (0, 0), overlay_image)

    # Save the image
    image.save(f'./database/activerenders/{save_dir}/{mode.lower()}.png')
