from io import BytesIO
from PIL import Image, ImageDraw, ImageFont
from calc.calcpractice import Practice
from helper.rendername import render_level_and_name
from helper.custombackground import background

def renderpractice(name, uuid, hypixel_data):
    # Open the image
    image_location = background(path='./assets/practice', uuid=uuid, default='base')
    image = Image.open(image_location)
    image = image.convert("RGBA")

    # Create an ImageDraw object
    draw = ImageDraw.Draw(image)

    # Choose a font and font size
    font = ImageFont.truetype('./assets/minecraft.ttf', 16)

    # Define the text colors
    green = (85, 255, 85)
    white = (255, 255, 255)
    black = (0, 0, 0)
    gold = (255, 170, 0)
    yellow = (255, 255, 85)
    red = (255, 85, 85)

    # Define the values
    practice = Practice(name, hypixel_data)
    level = practice.level
    player_rank_info = practice.get_player_rank_info()
    most_played = practice.get_most_played()

    bridging_completed, bridging_failed, bridging_blocks, bridging_ratio = practice.get_bridging_stats()
    tnt_completed, tnt_failed, tnt_blocks, tnt_ratio = practice.get_tnt_stats()
    mlg_completed, mlg_failed, mlg_blocks, mlg_ratio = practice.get_mlg_stats()
    straight_short, straight_medium, straight_long, straight_average = practice.get_straight_times()
    diagonal_short, diagonal_medium, diagonal_long, diagonal_average = practice.get_diagonal_times()

    totallength = draw.textlength(most_played, font=font) + draw.textlength("Most Played: ", font=font)
    most_played_x = int((image.width - totallength) / 2)

    data = (
        ((26, 137), (bridging_completed, green), "Completed: "),
        ((26, 163), (bridging_failed, red), "Failed: "),
        ((26, 189), (bridging_blocks, yellow), "Blocks: "),
        ((26, 215), (bridging_ratio, yellow), "C/F Ratio: "),
        ((231, 137), (tnt_completed, green), "Completed: "),
        ((231, 163), (tnt_failed, red), "Failed: "),
        ((231, 189), (tnt_blocks, yellow), "Blocks: "),
        ((231, 215), (tnt_ratio, yellow), "C/F Ratio: "),
        ((436, 137), (mlg_completed, green), "Completed: "),
        ((436, 163), (mlg_failed, red), "Failed: "),
        ((436, 189), (mlg_blocks, yellow), "Blocks: "),
        ((436, 215), (mlg_ratio, yellow), "C/F Ratio: "),
        ((26, 302), (straight_short, yellow), "Short: "),
        ((26, 328), (straight_medium, yellow), "Medium: "),
        ((26, 354), (straight_long, yellow), "Long: "),
        ((26, 380), (straight_average, yellow), "Average: "),
        ((335, 302), (diagonal_short, yellow), "Short: "),
        ((335, 328), (diagonal_medium, yellow), "Medium: "),
        ((335, 354), (diagonal_long, yellow), "Long: "),
        ((335, 380), (diagonal_average, yellow), "Average: "),
        ((most_played_x, 433), (most_played, gold), "Most Played: ")
    )

    for values in data:
        start_x, start_y = values[0]
        stat = values[1][0]
        text = values[2]

        draw.text((start_x + 2, start_y + 2), text, fill=black, font=font)
        draw.text((start_x, start_y), text, fill=white, font=font)

        start_x += draw.textlength(text, font=font)

        draw.text((start_x + 2, start_y + 2), stat, fill=black, font=font)
        draw.text((start_x, start_y), stat, fill=values[1][1], font=font)

    # Render the titles & name
    title_image = Image.open('./assets/practice/overlay.png')
    image.paste(title_image, (0, 0), title_image)

    player_y = 54
    render_level_and_name(name, level, player_rank_info, image=image, box_positions=(113, 415), position_y=player_y, fontsize=18)

    # Return the image
    image_bytes = BytesIO()
    image.save(image_bytes, format='PNG')
    image_bytes.seek(0)

    return image_bytes
