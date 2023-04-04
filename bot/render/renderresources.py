from PIL import Image, ImageDraw, ImageFont
from calc.calcresources import Resources
from helper.rendername import render_level_and_name
from helper.custombackground import background

def renderresources(name, uuid, mode, hypixel_data, save_dir):
    # Open the image
    image_location = background(path='./assets/resources', uuid=uuid, default='resources')
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
    gray = (170, 170, 170)
    gold = (255, 170, 0)
    aqua = (85, 255, 255)

    # Define the values
    resources = Resources(name, mode, hypixel_data)
    level = resources.level
    player_rank_info = resources.get_player_rank_info()

    iron_collected, gold_collected, diamonds_collected, emeralds_collected = resources.get_collected()

    iron_per_game, gold_per_game, diamonds_per_game, emeralds_per_game = resources.get_per_game()

    iron_per_star, gold_per_star, diamonds_per_star, emeralds_per_star = resources.get_per_star()

    iron_percentage = resources.get_iron_percentage()
    gold_percentage = resources.get_gold_percentage()
    diamond_percentage = resources.get_diamond_percentage()
    emerald_percentage = resources.get_emerald_percentage()

    total_collected = f'{resources.total_resources:,}'

    data = (
        ((68, 120), (iron_collected, gray), " Iron Collected"),
        ((68, 148), (gold_collected, gold), " Gold Collected"),
        ((68, 176), (diamonds_collected, aqua), " Diamonds Collected"),
        ((68, 204), (emeralds_collected, green), " Emeralds Collected"),
        ((360, 120), (iron_per_game, gray), " Iron / Game"),
        ((360, 148), (gold_per_game, gold), " Gold / Game"),
        ((360, 176), (diamonds_per_game, aqua), " Diamonds / Game"),
        ((360, 204), (emeralds_per_game, green), " Emeralds / Game"),
        ((68, 282), (iron_per_star, gray), " Iron / Star"),
        ((68, 310), (gold_per_star, gold), " Gold / Star"),
        ((68, 338), (diamonds_per_star, aqua), " Diamonds / Star"),
        ((68, 366), (emeralds_per_star, green), " Emeralds / Star"),
        ((360, 282), (iron_percentage, gray), " Iron"),
        ((360, 310), (gold_percentage, gold), " Gold"),
        ((360, 338), (diamond_percentage, aqua), " Diamonds"),
        ((360, 366), (emerald_percentage, green), " Emeralds"),
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

    # Unloopable stuff
    total_collected_txt = "Total Collected: "
    player_y = 48
    total_collected_y = 430

    # Render player name
    render_level_and_name(name, level, player_rank_info, image=image, box_positions=(101, 439), position_y=player_y, fontsize=18)

    # Render total
    totallength = draw.textlength(total_collected, font=font) + draw.textlength(total_collected_txt, font=font)
    startpoint = int((image.width - totallength) / 2)

    draw.text((startpoint + 2, total_collected_y + 2), total_collected_txt, fill=black, font=font)
    draw.text((startpoint, total_collected_y), total_collected_txt, fill=white, font=font)

    startpoint += draw.textlength(total_collected_txt, font=font)

    draw.text((startpoint + 2, total_collected_y + 2), total_collected, fill=black, font=font)
    draw.text((startpoint, total_collected_y), total_collected, fill=green, font=font)

    # Render the title
    title_txt = f"{mode.title()} Resources Collected"
    title_y = 19
    font = ImageFont.truetype('./assets/minecraft.ttf', 22)

    totallength = draw.textlength(title_txt, font=font)
    title_x = int((image.width - totallength) / 2)

    draw.text((title_x + 2, title_y + 2), title_txt, fill=black, font=font)
    draw.text((title_x, title_y), title_txt, fill=white, font=font)

    # Save the image
    image.save(f'./database/activerenders/{save_dir}/{mode.lower()}.png')
