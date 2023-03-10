import os
from PIL import Image, ImageDraw, ImageFont
from calc.calcsession import SessionStats
from helper.rendername import render_name
from helper.custombackground import background

def rendersession(name, uuid, session, mode, hypixel_data, save_dir):
    image_location = background(path=f'{os.getcwd()}/assets/session', uuid=uuid, default='session')
    image = Image.open(image_location)
    image = image.convert("RGBA")

    draw = ImageDraw.Draw(image)

    font = ImageFont.truetype(f'{os.getcwd()}/assets/minecraft.ttf', 16)

    # Define the text colors
    green = (85, 255, 85)
    white = (255, 255, 255)
    red = (255, 76, 76)
    yellow = (255, 255, 81)
    black = (0, 0, 0)
    blue = (79, 79, 255)

    # Get stats
    stats = SessionStats(name, uuid, session, mode, hypixel_data)

    player_rank = stats.get_player_rank()
    most_played = stats.get_most_played()
    level = stats.level
    date_started = stats.date_started

    wins, losses, wlr = stats.get_wins()
    final_kills, final_deaths, fkdr = stats.get_finals()
    beds_broken, beds_lost, bblr = stats.get_beds()
    kills, deaths, kdr = stats.get_kills()
    wins_per_day, finals_per_day, beds_per_day, stars_per_day = stats.get_per_day()

    data = (
        ((42, 148), (wins, green), " Wins"),
        ((42, 179), (losses, red), " Losses"),
        ((42, 210), (wlr, yellow), " WLR"),
        ((198, 148), (final_kills, green), " Final Kills"),
        ((198, 179), (final_deaths, red), " Final Deaths"),
        ((198, 210), (fkdr, yellow), " FKDR"),
        ((198, 283), (beds_broken, green), " Beds Broken"),
        ((198, 315), (beds_lost, red), " Beds Lost"),
        ((198, 347), (bblr, yellow), " BBLR"),
        ((42, 283), (kills, green), " Kills"),
        ((42, 315), (deaths, red), " Deaths"),
        ((42, 347), (kdr, yellow), " KDR"),
        ((427, 146), (wins_per_day, blue), " Wins / Day"),
        ((427, 178), (finals_per_day, blue), " Finals / Day"),
        ((427, 208), (beds_per_day, blue), " Beds / Day"),
        ((427, 283), (stars_per_day, blue), " Stars / Day"),
        ((427, 315), (stats.stars_gained, blue), " Stars Gained"),
        ((427, 345), (stats.games_played, blue), " Games Played"),
    )

    for values in data:
        start_x, start_y = values[0]
        stat = values[1][0]
        text = values[2]

        draw.text((start_x + 2, start_y + 2), stat, fill=black, font=font)
        draw.text((start_x, start_y), stat, fill=values[1][1], font=font)

        start_x += draw.textlength(stat, font=font)

        draw.text((start_x + 2, start_y + 2), text, fill=black, font=font)
        draw.text((start_x, start_y), text, fill=white, font=font)


    # Unloopables
    started_txt = " Started"
    most_played_txt = " Most Played"

    player_y = 74

    started_x = 76
    started_y = 412

    mostplayed_x = 336
    mostplayed_y = 412


    # Render the complex bottom stuff
    # Started
    totallength = draw.textlength(date_started, font=font) + draw.textlength(started_txt, font=font)
    started_x = int((248 - totallength) / 2) + started_x

    draw.text((started_x + 2, started_y + 2), date_started, fill=black, font=font)
    draw.text((started_x, started_y), date_started, fill=blue, font=font)

    started_x += draw.textlength(date_started, font=font)

    draw.text((started_x + 2, started_y+ 2), started_txt, fill=black, font=font)
    draw.text((started_x, started_y), started_txt, fill=white, font=font)

    # Most played
    totallength = draw.textlength(most_played, font=font) + draw.textlength(most_played_txt, font=font)
    mostplayed_x = int((227 - totallength) / 2) + mostplayed_x

    draw.text((mostplayed_x + 2, mostplayed_y + 2), most_played, fill=black, font=font)
    draw.text((mostplayed_x, mostplayed_y), most_played, fill=blue, font=font)

    mostplayed_x += draw.textlength(most_played, font=font)

    draw.text((mostplayed_x + 2, mostplayed_y + 2), most_played_txt, fill=black, font=font)
    draw.text((mostplayed_x, mostplayed_y), most_played_txt, fill=white, font=font)


    # Render the name and title
    title_txt = f"{mode.title()} Bedwars Session # {session}"
    title_y = 40
    font = ImageFont.truetype(f'{os.getcwd()}/assets/minecraft.ttf', 24)

    totallength = draw.textlength(title_txt, font=font)
    title_x = int((image.width - totallength) / 2)

    draw.text((title_x + 2, title_y + 2), title_txt, fill=black, font=font)
    draw.text((title_x, title_y), title_txt, fill=white, font=font)

    render_name(name, level, player_rank, image, player_y, fontsize=20)

    # Save the image
    image.save(f'{os.getcwd()}/database/activerenders/{save_dir}/{mode.lower()}.png')
