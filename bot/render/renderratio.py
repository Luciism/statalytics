from PIL import Image, ImageDraw, ImageFont
from calc.calcratio import Ratios
from helper.rendername import render_level_and_name
from helper.custombackground import background

def renderratio(name, uuid, mode, hypixel_data, save_dir):
    # Open the image
    image_location = background(path='./assets/ratios', uuid=uuid, default='ratios')
    image = Image.open(image_location)
    image = image.convert("RGBA")

    # Create an ImageDraw object
    draw = ImageDraw.Draw(image)

    # Choose a font and font size
    font = ImageFont.truetype('./assets/minecraft.ttf', 16)

    # Define the text colors
    green = (85, 255, 85)
    white = (255, 255, 255)
    red = (255, 76, 76)
    black = (0, 0, 0)

    # Define the values
    ratios = Ratios(name, mode, hypixel_data)
    level = ratios.level
    player_rank_info = ratios.get_player_rank_info()
    (
        wins_per_star,
        final_kills_per_star,
        beds_broken_per_star,
        kills_per_star,
        losses_per_star,
        final_deaths_per_star,
        beds_lost_per_star,
        deaths_per_star
    ) = ratios.get_per_star()

    (
        final_kills_per_game,
        beds_broken_per_game,
        kills_per_game,
        final_deaths_per_game,
        beds_lost_per_game,
        deaths_per_game,
    ) = ratios.get_per_game()


    clutch_rate = ratios.get_clutch_rate()
    loss_rate = ratios.get_loss_rate()

    most_wins = ratios.get_most_wins()
    most_losses = ratios.get_most_losses()

    data = (
        ((72, 135), (wins_per_star, green), " Wins / Star"),
        ((72, 163), (final_kills_per_star, green), " Final K / Star"),
        ((72, 191), (beds_broken_per_star, green), " Beds B / Star"),
        ((72, 219), (kills_per_star, green), " Kills / Star"),
        ((354, 135), (final_kills_per_game, green), " Final K / Game"),
        ((354, 163), (beds_broken_per_game, green), " Beds B / Game"),
        ((354, 191), (kills_per_game, green), " Kills / Game"),
        ((354, 219), (clutch_rate, green), " Clutch Rate"),
        ((72, 279), (losses_per_star, red), " Losses / Star"),
        ((72, 307), (final_deaths_per_star, red), " Final D / Star"),
        ((72, 335), (beds_lost_per_star, red), " Beds L / Star"),
        ((72, 363), (deaths_per_star, red), " Deaths / Star"),
        ((351, 279), (final_deaths_per_game, red), " Final D / Game"),
        ((351, 307), (beds_lost_per_game, red), " Beds L / Game"),
        ((351, 335), (deaths_per_game, red), " Deaths / Game"),
        ((351, 363), (loss_rate, red), " Loss Rate")
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

    # Second half (describe)
    most_wins_txt = "Most Wins: "
    most_losses_txt = "Most Losses: "

    # Calculate the position of the text
    player_y = 70
    most_y = 420


    # Render player name
    render_level_and_name(name, level, player_rank_info, image=image, box_positions=(106, 428), position_y=player_y, fontsize=20)

    # Render most wins and losses
    totallength = draw.textlength(f"{most_wins_txt}{most_wins}", font=font)
    startpoint = int((235 - totallength) / 2) + 81

    draw.text((startpoint + 2, most_y + 2), most_wins_txt, fill=black, font=font)
    draw.text((startpoint, most_y), most_wins_txt, fill=white, font=font)

    startpoint += draw.textlength(most_wins_txt, font=font)

    draw.text((startpoint + 2, most_y + 2), most_wins, fill=black, font=font)
    draw.text((startpoint, most_y), most_wins, fill=green, font=font)

    totallength = draw.textlength(f"{most_losses_txt}{most_losses}", font=font)
    startpoint = int((235 - totallength) / 2) + 324

    draw.text((startpoint + 2, most_y + 2), most_losses_txt, fill=black, font=font)
    draw.text((startpoint, most_y), most_losses_txt, fill=white, font=font)

    startpoint += draw.textlength(most_losses_txt, font=font)

    draw.text((startpoint + 2, most_y + 2), most_losses, fill=black, font=font)
    draw.text((startpoint, most_y), most_losses, fill=red, font=font)


    # Render the title
    title_txt = f"{mode.title()} Bedwars Averages"
    title_y = 37
    font = ImageFont.truetype('./assets/minecraft.ttf', 24)

    totallength = draw.textlength(title_txt, font=font)
    title_x = int((image.width - totallength) / 2)

    draw.text((title_x + 2, title_y + 2), title_txt, fill=black, font=font)
    draw.text((title_x, title_y), title_txt, fill=white, font=font)

    # Save the image
    image.save(f'./database/activerenders/{save_dir}/{mode.lower()}.png')
