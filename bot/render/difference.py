from PIL import Image, ImageDraw, ImageFont

from calc.difference import Difference
from helper.rendername import get_rank_prefix, render_rank
from helper.rendertools import get_background, paste_skin, box_center_text
from helper.renderprogress import render_progress_bar, render_progress_text


def render_difference(name, uuid, relative_date, method,
                      mode, hypixel_data, skin_res, save_dir):
    diffs = Difference(name, uuid, method, mode, hypixel_data)

    level = diffs.level
    player_rank_info = diffs.player_rank_info
    progress, target, progress_out_of_10 = diffs.progress
    stars_gained = diffs.get_stars_gained()

    wins, losses, wlr_1, wlr_2, wlr_diff = diffs.get_wins()
    final_kills, final_deaths, fkdr_1, fkdr_2, fkdr_diff = diffs.get_finals()
    beds_broken, beds_lost, bblr_1, bblr_2, bblr_diff = diffs.get_beds()
    kills, deaths, kdr_1, kdr_2, kdr_diff = diffs.get_kills()

    green = (85, 255, 85)
    white = (255, 255, 255)
    red = (255, 76, 76)
    black = (0, 0, 0)
    light_purple = (255, 85, 255)
    gold = (255, 170, 0)

    image = get_background(path='./assets/bg/difference', uuid=uuid,
                           default='base', level=level, rank_info=player_rank_info)
    image = image.convert("RGBA")

    draw = ImageDraw.Draw(image)
    minecraft_16 = ImageFont.truetype('./assets/minecraft.ttf', 16)
    minecraft_18 = ImageFont.truetype('./assets/minecraft.ttf', 18)
    minecraft_22 = ImageFont.truetype('./assets/minecraft.ttf', 22)

    def leng(text, width):
        return (width - draw.textlength(text, font=minecraft_16)) / 2

    def diff_color(diff: str) -> tuple:
        if diff[1] == '+':
            return green
        return red

    data = (
        ((leng(wins, 141)+18, 249), ((wins, green),)),
        ((leng(final_kills, 141)+18, 309), ((final_kills, green),)),
        ((leng(beds_broken, 141)+18, 369), ((beds_broken, green),)),
        ((leng(kills, 141)+18, 429), ((kills, green),)),

        ((leng(losses, 141)+172, 249), ((losses, red),)),
        ((leng(final_deaths, 141)+172, 309), ((final_deaths, red),)),
        ((leng(beds_lost, 141)+172, 369), ((beds_lost, red),)),
        ((leng(deaths, 141)+172, 429), ((deaths, red),)),

        ((leng(f'{wlr_1} -> {wlr_2} {wlr_diff}', 296)+326, 249),
         ((wlr_1, gold), (' -> ', white), (wlr_2, gold), (f' {wlr_diff}', diff_color(wlr_diff)))),

        ((leng(f'{fkdr_1} -> {fkdr_2} {fkdr_diff}', 296)+326, 309),
         ((fkdr_1, gold), (' -> ', white), (fkdr_2, gold), (f' {fkdr_diff}', diff_color(fkdr_diff)))),

        ((leng(f'{bblr_1} -> {bblr_2} {bblr_diff}', 296)+326, 369),
         ((bblr_1, gold), (' -> ', white), (bblr_2, gold), (f' {bblr_diff}', diff_color(bblr_diff)))),

        ((leng(f'{kdr_1} -> {kdr_2} {kdr_diff}', 296)+326, 429),
         ((kdr_1, gold), (' -> ', white), (kdr_2, gold), (f' {kdr_diff}', diff_color(kdr_diff)))),

        ((leng(stars_gained, 201)+18, 189), ((stars_gained, light_purple),)),
        ((leng(relative_date, 201)+232, 189), ((relative_date, light_purple),)),
        ((leng(f'({mode.title()})', 171)+451, 46), ((f'({mode.title()})', white),))
    )

    for values in data:
        start_x, start_y = values[0]
        texts = values[1]

        for text in texts:
            draw.text((start_x + 2, start_y + 2), text[0], fill=black, font=minecraft_16)
            draw.text((start_x, start_y), text[0], fill=text[1], font=minecraft_16)

            start_x += draw.textlength(text[0], font=minecraft_16)

    # Render name & progress bar
    rank_prefix = get_rank_prefix(player_rank_info)
    totallength = draw.textlength(f'{rank_prefix}{name}', font=minecraft_22)
    player_x = round((415 - totallength) / 2) + 18

    render_rank(name, position_x=player_x, position_y=26, rank_prefix=rank_prefix,
                player_rank_info=player_rank_info, draw=draw, fontsize=22)

    render_progress_bar(box_positions=(415, 18), position_y=88, level=level,
                        progress_out_of_10=progress_out_of_10, image=image)

    render_progress_text(box_positions=(415, 18), position_y=119,
                         progress=progress, target=target, draw=draw)

    # Paste overlay
    overlay_image = Image.open('./assets/bg/difference/overlay.png')
    overlay_image = overlay_image.convert("RGBA")
    image.paste(overlay_image, (0, 0), overlay_image)

    box_center_text(f"{method.title()} Diffs", draw, box_width=171,
                    box_start=451, text_y=25, font=minecraft_18)

    # Render skin
    image = paste_skin(skin_res, image, positions=(465, 67))

    # Save the image
    image.save(f'./database/activerenders/{save_dir}/{mode.lower()}.png')
