from io import BytesIO
from PIL import Image, ImageDraw, ImageFont
from calc.historical import HistoricalStats, LookbackStats
from helper.rendername import render_rank, get_rank_prefix, paste_skin
from helper.custombackground import background
from helper.renderprogress import render_progress_bar, render_progress_text

def render_historical(name, uuid, method, mode, hypixel_data, skin_res, save_dir, table_name = None):
    # Open the image
    image_location = background(path='./assets/historical', uuid=uuid, default=f'base_{method}')
    image = Image.open(image_location)
    image = image.convert("RGBA")

    # Create an ImageDraw object
    draw = ImageDraw.Draw(image)

    # Choose a font and font size
    minecraft_16 = ImageFont.truetype('./assets/minecraft.ttf', 16)
    minecraft_17 = ImageFont.truetype('./assets/minecraft.ttf', 17)
    minecraft_22 = ImageFont.truetype('./assets/minecraft.ttf', 22)

    # Define the text colors
    green = (85, 255, 85)
    white = (255, 255, 255)
    red = (255, 76, 76)
    black = (0, 0, 0)
    gold = (255, 170, 0)
    light_purple = (255, 85, 255)

    if not table_name:
        stats = HistoricalStats(name, uuid, method, mode, hypixel_data)
    else:
        stats = LookbackStats(name, uuid, table_name, mode, hypixel_data)
        title_map = {
            "yesterday": "Yesterday",
            "lastweek": "Last Week",
            "lastmonth": "Last Month",
            "lastyear": "Last Year"
        }

    level = stats.level
    player_rank_info = stats.player_rank_info

    progress, target, progress_out_of_10 = stats.progress
    todays_date, timezone, reset_hour = stats.get_time_info()
    most_played = stats.get_most_played()
    games_played = f'{stats.games_played:,}'
    items_purchased = f'{stats.items_purchased:,}'
    stars_gained = stats.stars_gained

    wins, losses, wlr = stats.get_wins()
    final_kills, final_deaths, fkdr = stats.get_finals()
    beds_broken, beds_lost, bblr = stats.get_beds()
    kills, deaths, kdr = stats.get_kills()

    def leng(text, width):
        return (width - draw.textlength(text, font=ImageFont.truetype('./assets/minecraft.ttf', 16))) / 2

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
        ((leng(stars_gained, 130) + 17, 427), (stars_gained, light_purple)),
        ((leng(timezone, 127) + 163, 427), (timezone, light_purple)),
        ((leng(reset_hour, 128) + 306, 427), (reset_hour, light_purple)),
        ((leng(games_played, 171) + 452, 249), (games_played, light_purple)),
        ((leng(most_played, 171) + 452, 308), (most_played, light_purple)),
        ((leng(todays_date, 171) + 452, 367), (todays_date, light_purple)),
        ((leng(items_purchased, 171) + 452, 427), (items_purchased, light_purple)),
        ((leng(f'({mode.title()})', 171) + 452, 46), (f'({mode.title()})', white)),
    )

    for values in data:
        start_x, start_y = values[0]
        stat = values[1][0]

        draw.text((start_x + 2, start_y + 2), stat, fill=black, font=minecraft_16)
        draw.text((start_x, start_y), stat, fill=values[1][1], font=minecraft_16)

    # Render the player name
    rank_prefix = get_rank_prefix(player_rank_info)
    totallength = draw.textlength(f'{rank_prefix}{name}', font=minecraft_22)
    player_x = round((415 - totallength) / 2) + 19
    render_rank(name, position_x=player_x, position_y=31, rank_prefix=rank_prefix, player_rank_info=player_rank_info, draw=draw, fontsize=22)

    # Render the progress
    render_progress_bar(box_positions=(415, 19), position_y=91, level=level, progress_out_of_10=progress_out_of_10, image=image)
    render_progress_text(box_positions=(415, 19), position_y=122, progress=progress, target=target, draw=draw)

    paste_skin(skin_res, image, positions=(466, 69))

    # Draw title
    title = f'{method.title()} BW Stats' if not table_name else title_map.get(method)
    totallength = draw.textlength(title, font=minecraft_17)
    title_x = round((171 - totallength) / 2) + 452
    title_y = 27
    draw.text((title_x + 2, title_y + 2), title, fill=black, font=minecraft_17)
    draw.text((title_x, title_y), title, fill=white, font=minecraft_17)

    # Paste overlay
    overlay_image = Image.open(f'./assets/historical/overlay.png')
    overlay_image = overlay_image.convert("RGBA")
    image.paste(overlay_image, (0, 0), overlay_image)

    # Save the image
    image.save(f'./database/activerenders/{save_dir}/{mode.lower()}.png')
