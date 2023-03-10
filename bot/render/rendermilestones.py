import os
from PIL import Image, ImageDraw, ImageFont
from helper.rendername import render_name, render_level
from calc.calcmilestones import Stats
from helper.custombackground import background

def rendermilestones(name, uuid, mode, hypixel_data, save_dir):
    image_location = background(path=f'{os.getcwd()}/assets/milestones', uuid=uuid, default='milestones')
    image = Image.open(image_location)
    image = image.convert("RGBA")

    draw = ImageDraw.Draw(image)

    font = ImageFont.truetype(f'{os.getcwd()}/assets/minecraft.ttf', 16)

    green = (85, 255, 85)
    white = (255, 255, 255)
    black = (0, 0, 0)
    gray = (170, 170, 170)
    yellow = (255, 255, 85)
    red = (255, 85, 85)

    stats = Stats(name, uuid, mode, hypixel_data)
    level = stats.level
    playerrank = stats.get_player_rank()

    # --
    wins_ratio_target = stats.get_wlr_target()
    final_kills_ratio_target = stats.get_fkdr_target()
    beds_broken_ratio_target = stats.get_bblr_target()
    kills_ratio_target = stats.get_kdr_target()

    stars_until_value = stats.get_stars_value()
    stars_until_target = stats.get_stars_target()

    # Get values for each stat
    data = (
        ((27, 125), (stats.get_wins_until_value(), green), wins_ratio_target, " Wins Until "),
        ((27, 154), (stats.get_wins_at_value(), green), wins_ratio_target, " Wins At "),
        ((27, 183), (stats.get_wins_until_value(), green), stats.get_wins_until_wins_target(), " Wins Until "),
        ((27, 212), (stats.get_losses_until_losses_value(), red), stats.get_losses_until_losses_target(), " Losses Until "),
        ((336, 125), (stats.get_final_kills_until_value(), green), final_kills_ratio_target, " Final K Until "),
        ((336, 154), (stats.get_final_kills_at_value(), green), final_kills_ratio_target, " Final K At "),
        ((336, 183), (stats.get_final_kills_until_final_kills_value(), green), stats.get_final_kills_until_final_kills_target(), " Final K Until "),
        ((336, 212), (stats.get_final_deaths_until_final_deaths_value(), red), stats.get_final_deaths_until_final_deaths_target(), " Final D Until "),
        ((27, 287), (stats.get_beds_broken_until_value(), green), beds_broken_ratio_target, " Beds B Until "),
        ((27, 316), (stats.get_beds_broken_at_value(), green), beds_broken_ratio_target, " Beds B At "),
        ((27, 345), (stats.get_beds_broken_until_beds_broken_value(), green), stats.get_beds_broken_until_beds_broken_target(), " Beds B Until "),
        ((27, 374), (stats.get_beds_lost_until_beds_lost_value(), red), stats.get_beds_lost_until_beds_lost_target(), " Beds L Until "),
        ((336, 287), (stats.get_kills_until_value(), green), kills_ratio_target, " Kills Until "),
        ((336, 316), (stats.get_kills_at_value(), green), kills_ratio_target, " Kills At "),
        ((336, 345), (stats.get_kills_until_kills_value(), green), stats.get_kills_until_kills_target(), " Kills Until "),
        ((336, 374), (stats.get_deaths_until_deaths_value(), red), stats.get_deaths_until_deaths_target(), " Deaths Until ")
    )

    # Render stats
    for values in data:
        start_x, start_y = values[0]
        stat_1 = values[1][0]
        stat_2 = values[2]
        text = values[3]

        draw.text((start_x + 2, start_y + 2), stat_1, fill=black, font=font)
        draw.text((start_x, start_y), stat_1, fill=values[1][1], font=font)

        start_x += draw.textlength(stat_1, font=font)

        draw.text((start_x + 2, start_y + 2), text, fill=black, font=font)
        draw.text((start_x, start_y), text, fill=white, font=font)

        start_x += draw.textlength(text, font=font)

        draw.text((start_x + 2, start_y + 2), stat_2, fill=black, font=font)
        draw.text((start_x, start_y), stat_2, fill=yellow, font=font)


    # Things that cant be done in the loop
    player_y = 54
    stars_until_y = 435
    stars_until_txt = " Stars Until "

    # Render Stars Stats
    totallength = draw.textlength(stars_until_value, font=font) + draw.textlength(stars_until_txt, font=font) + draw.textlength(str(stars_until_target), font=font) + draw.textlength("[]") + 16
    stars_until_x = int((image.width - totallength) / 2)

    draw.text((stars_until_x + 2, stars_until_y + 2), stars_until_value, fill=black, font=font)
    draw.text((stars_until_x, stars_until_y), stars_until_value, fill=gray, font=font)

    stars_until_x += draw.textlength(stars_until_value, font=font)

    draw.text((stars_until_x + 2, stars_until_y + 2), stars_until_txt, fill=black, font=font)
    draw.text((stars_until_x, stars_until_y), stars_until_txt, fill=white, font=font)

    stars_until_x += draw.textlength(stars_until_txt, font=font)
    render_level(level=int(stars_until_target), image=image, startpoint=stars_until_x, startpoint_y=stars_until_y, fontsize=16)

    # Render the title
    title_txt = f"{mode.title()} Milestone Progress"
    title_y = 23
    font = ImageFont.truetype(f'{os.getcwd()}/assets/minecraft.ttf', 24)

    totallength = draw.textlength(title_txt, font=font)
    title_x = int((image.width - totallength) / 2)

    draw.text((title_x + 2, title_y + 2), title_txt, fill=black, font=font)
    draw.text((title_x, title_y), title_txt, fill=white, font=font)

    # Render player name
    render_name(name, level, playerrank, image, player_y, fontsize=20)

    image.save(f'{os.getcwd()}/database/activerenders/{save_dir}/{mode.lower()}.png')
