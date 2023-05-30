from PIL import ImageDraw, ImageFont
from calc.milestones import Stats
from helper.rendername import render_level, get_rank_prefix, render_rank
from helper.rendertools import get_background, paste_skin, box_center_text
from helper.renderprogress import render_progress_bar, render_progress_text


def render_milestones(name, uuid, mode, session, hypixel_data, skin_res, save_dir):
    stats = Stats(name, uuid, mode, session, hypixel_data)
    level = stats.level
    player_rank_info = stats.player_rank_info
    stars_until_value, stars_until_target = stats.get_stars()
    progress, target, progress_out_of_10 = stats.progress

    wins_until_wlr, wins_at_wlr, target_wlr, wins_until_wins, target_wins, losses_until_losses, target_losses = stats.get_wins()
    final_kills_until_fkdr, final_kills_at_fkdr, target_fkdr, final_kills_until_final_kills, target_final_kills, final_deaths_until_final_deaths, target_final_deaths = stats.get_finals()
    beds_broken_until_bblr, beds_broken_at_bblr, target_bblr, beds_broken_until_beds_broken, target_beds_broken, beds_lost_until_beds_lost, target_beds_lost = stats.get_beds()
    kills_until_kdr, kills_at_kdr, target_kdr, kills_until_kills, target_kills, deaths_until_deaths, target_deaths = stats.get_kills()

    green = (85, 255, 85)
    white = (255, 255, 255)
    black = (0, 0, 0)
    gray = (170, 170, 170)
    gold = (255, 170, 0)
    red = (255, 85, 85)

    data = (
        ((31, 212), (wins_until_wlr, green), target_wlr, " Wins Until "),
        ((31, 241), (wins_at_wlr, green), target_wlr, " Wins At "),
        ((31, 270), (wins_until_wins, green), target_wins, " Wins Until "),
        ((31, 299), (losses_until_losses, red), target_losses, " Losses Until "),
        ((342, 212), (final_kills_until_fkdr, green), target_fkdr, " Final K Until "),
        ((342, 241), (final_kills_at_fkdr, green), target_fkdr, " Final K At "),
        ((342, 270), (final_kills_until_final_kills, green), target_final_kills, " Final K Until "),
        ((342, 299), (final_deaths_until_final_deaths, red), target_final_deaths, " Final D Until "),
        ((31, 343), (beds_broken_until_bblr, green), target_bblr, " Beds B Until "),
        ((31, 372), (beds_broken_at_bblr, green), target_bblr, " Beds B At "),
        ((31, 401), (beds_broken_until_beds_broken, green), target_beds_broken, " Beds B Until "),
        ((31, 430), (beds_lost_until_beds_lost, red), target_beds_lost, " Beds L Until "),
        ((342, 343), (kills_until_kdr, green), target_kdr, " Kills Until "),
        ((342, 372), (kills_at_kdr, green), target_kdr, " Kills At "),
        ((342, 401), (kills_until_kills, green), target_kills, " Kills Until "),
        ((342, 430), (deaths_until_deaths, red), target_deaths, " Deaths Until ")
    )

    image = get_background(path='./assets/milestones', uuid=uuid, default='base', level=level, rank_info=player_rank_info)
    image = image.convert("RGBA")

    draw = ImageDraw.Draw(image)
    minecraft_16 = ImageFont.truetype('./assets/minecraft.ttf', 16)
    minecraft_18 = ImageFont.truetype('./assets/minecraft.ttf', 18)
    minecraft_22 = ImageFont.truetype('./assets/minecraft.ttf', 22)

    for values in data:
        start_x, start_y = values[0]
        stat_1 = values[1][0]
        stat_2 = values[2]
        text = values[3]

        draw.text((start_x + 2, start_y + 2), stat_1, fill=black, font=minecraft_16)
        draw.text((start_x, start_y), stat_1, fill=values[1][1], font=minecraft_16)

        start_x += draw.textlength(stat_1, font=minecraft_16)

        draw.text((start_x + 2, start_y + 2), text, fill=black, font=minecraft_16)
        draw.text((start_x, start_y), text, fill=white, font=minecraft_16)

        start_x += draw.textlength(text, font=minecraft_16)

        draw.text((start_x + 2, start_y + 2), stat_2, fill=black, font=minecraft_16)
        draw.text((start_x, start_y), stat_2, fill=gold, font=minecraft_16)


    # Things that cant be done in the loop
    stars_until_y = 169
    stars_until_txt = " Stars Until "

    # Render Stars Stats
    totallength = draw.textlength(f'[{stars_until_value}]{stars_until_txt}{stars_until_target}', font=minecraft_16) + 16
    stars_until_x = int((415 - totallength) / 2) + 18

    draw.text((stars_until_x + 2, stars_until_y + 2), stars_until_value, fill=black, font=minecraft_16)
    draw.text((stars_until_x, stars_until_y), stars_until_value, fill=gray, font=minecraft_16)

    stars_until_x += draw.textlength(stars_until_value, font=minecraft_16)

    draw.text((stars_until_x + 2, stars_until_y + 2), stars_until_txt, fill=black, font=minecraft_16)
    draw.text((stars_until_x, stars_until_y), stars_until_txt, fill=white, font=minecraft_16)

    stars_until_x += draw.textlength(stars_until_txt, font=minecraft_16)
    render_level(level=int(stars_until_target), position_x=stars_until_x, position_y=stars_until_y, fontsize=16, image=image)

    # Render the player name
    rank_prefix = get_rank_prefix(player_rank_info)
    totallength = draw.textlength(f'{rank_prefix}{name}', font=minecraft_22)
    player_x = round((415 - totallength) / 2) + 19
    render_rank(name, position_x=player_x, position_y=28, rank_prefix=rank_prefix, player_rank_info=player_rank_info, draw=draw, fontsize=22)

    # Render the progress
    render_progress_bar(box_positions=(415, 18), position_y=89, level=level, progress_out_of_10=progress_out_of_10, image=image)
    render_progress_text(box_positions=(415, 18), position_y=120, progress=progress, target=target, draw=draw)

    box_center_text('Milestones', draw, box_width=171, box_start=451, text_y=23, font=minecraft_18)
    box_center_text(f'({mode.title()})', draw, box_width=171, box_start=451, text_y=45, font=minecraft_16)

    image = paste_skin(skin_res, image, positions=(472, 61))

    image.save(f'./database/activerenders/{save_dir}/{mode.lower()}.png')
