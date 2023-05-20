from PIL import Image, ImageDraw, ImageFont
from helper.rendername import render_level_and_name, render_level
from calc.milestones import Stats
from helper.custombackground import background

def render_milestones(name, uuid, mode, session, hypixel_data, save_dir):
    image_location = background(path='./assets/milestones', uuid=uuid, default='base')
    image = Image.open(image_location)
    image = image.convert("RGBA")

    draw = ImageDraw.Draw(image)

    font = ImageFont.truetype('./assets/minecraft.ttf', 16)

    green = (85, 255, 85)
    white = (255, 255, 255)
    black = (0, 0, 0)
    gray = (170, 170, 170)
    yellow = (255, 255, 85)
    red = (255, 85, 85)

    stats = Stats(name, uuid, mode, session, hypixel_data)
    level = stats.level
    player_rank_info = stats.player_rank_info

    wins_until_wlr, wins_at_wlr, target_wlr, wins_until_wins, target_wins, losses_until_losses, target_losses = stats.get_wins()
    final_kills_until_fkdr, final_kills_at_fkdr, target_fkdr, final_kills_until_final_kills, target_final_kills, final_deaths_until_final_deaths, target_final_deaths = stats.get_finals()
    beds_broken_until_bblr, beds_broken_at_bblr, target_bblr, beds_broken_until_beds_broken, target_beds_broken, beds_lost_until_beds_lost, target_beds_lost = stats.get_beds()
    kills_until_kdr, kills_at_kdr, target_kdr, kills_until_kills, target_kills, deaths_until_deaths, target_deaths = stats.get_kills()

    stars_until_value, stars_until_target = stats.get_stars()

    # Get values for each stat
    data = (
        ((27, 125), (wins_until_wlr, green), target_wlr, " Wins Until "),
        ((27, 154), (wins_at_wlr, green), target_wlr, " Wins At "),
        ((27, 183), (wins_until_wins, green), target_wins, " Wins Until "),
        ((27, 212), (losses_until_losses, red), target_losses, " Losses Until "),
        ((336, 125), (final_kills_until_fkdr, green), target_fkdr, " Final K Until "),
        ((336, 154), (final_kills_at_fkdr, green), target_fkdr, " Final K At "),
        ((336, 183), (final_kills_until_final_kills, green), target_final_kills, " Final K Until "),
        ((336, 212), (final_deaths_until_final_deaths, red), target_final_deaths, " Final D Until "),
        ((27, 287), (beds_broken_until_bblr, green), target_bblr, " Beds B Until "),
        ((27, 316), (beds_broken_at_bblr, green), target_bblr, " Beds B At "),
        ((27, 345), (beds_broken_until_beds_broken, green), target_beds_broken, " Beds B Until "),
        ((27, 374), (beds_lost_until_beds_lost, red), target_beds_lost, " Beds L Until "),
        ((336, 287), (kills_until_kdr, green), target_kdr, " Kills Until "),
        ((336, 316), (kills_at_kdr, green), target_kdr, " Kills At "),
        ((336, 345), (kills_until_kills, green), target_kills, " Kills Until "),
        ((336, 374), (deaths_until_deaths, red), target_deaths, " Deaths Until ")
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
    totallength = draw.textlength(f'[{stars_until_value}]{stars_until_txt}{stars_until_target}', font=font) + 16
    stars_until_x = int((image.width - totallength) / 2)

    draw.text((stars_until_x + 2, stars_until_y + 2), stars_until_value, fill=black, font=font)
    draw.text((stars_until_x, stars_until_y), stars_until_value, fill=gray, font=font)

    stars_until_x += draw.textlength(stars_until_value, font=font)

    draw.text((stars_until_x + 2, stars_until_y + 2), stars_until_txt, fill=black, font=font)
    draw.text((stars_until_x, stars_until_y), stars_until_txt, fill=white, font=font)

    stars_until_x += draw.textlength(stars_until_txt, font=font)
    render_level(level=int(stars_until_target), position_x=stars_until_x, position_y=stars_until_y, fontsize=16, image=image)

    # Render the title
    title_txt = f"{mode.title()} Milestone Progress"
    title_y = 23
    font = ImageFont.truetype('./assets/minecraft.ttf', 24)

    totallength = draw.textlength(title_txt, font=font)
    title_x = int((image.width - totallength) / 2)

    draw.text((title_x + 2, title_y + 2), title_txt, fill=black, font=font)
    draw.text((title_x, title_y), title_txt, fill=white, font=font)

    # Render player name
    render_level_and_name(name, level, player_rank_info, image=image, box_positions=(91, 450), position_y=player_y, fontsize=20)

    image.save(f'./database/activerenders/{save_dir}/{mode.lower()}.png')
