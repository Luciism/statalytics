from io import BytesIO

from PIL import Image, ImageDraw, ImageFont

from statalib import get_rank_info, to_thread
from statalib.render import get_background, get_rank_color


@to_thread
def render_mostplayed(name, uuid, hypixel_data):
    hypixel_data = hypixel_data.get('player', {})\
                   if hypixel_data.get('player', {}) is not None else {}

    solos = hypixel_data.get('stats', {}).get('Bedwars', {}).get('eight_one_games_played_bedwars', 1)
    doubles = hypixel_data.get('stats', {}).get('Bedwars', {}).get('eight_two_games_played_bedwars', 1)
    threes = hypixel_data.get('stats', {}).get('Bedwars', {}).get('four_three_games_played_bedwars', 1)
    fours = hypixel_data.get('stats', {}).get('Bedwars', {}).get('four_four_games_played_bedwars', 1)

    rank_info = get_rank_info(hypixel_data=hypixel_data)
    rankcolor = get_rank_color(rank_info)

    # Get ratio
    numbers = [int(solos), int(doubles), int(threes), int(fours)]
    total = sum(numbers)
    ratios = [num / total for num in numbers]

    color = (45, 45, 255, 127)

    # Define the coordinates for the bars
    positions = [(97, 354), (220, 354), (343, 354), (466, 354)]

    # Open Images
    base_image = get_background(path='./assets/bg/mostplayed', uuid=uuid,
                                default='base', level=0, rank_info=rank_info)

    base_image = base_image.convert("RGBA")

    bar_graph = Image.new('RGBA', (640, 420), (0, 0, 0, 0))
    draw = ImageDraw.Draw(bar_graph)

    # Draw the bars
    if max(ratios) * 500 > 250:
        difference = (max(ratios) * 500) - 250
        ratios = [value - (difference / 500)
                  if value - (difference / 500) > 0 else 0 for value in ratios]


    for i, value in enumerate(ratios):
        height = 250 if value * 500 > 250 else value * 500
        draw.rectangle([(positions[i][0] + 77, positions[i][1] - height), positions[i]], fill=color)

    base_image = Image.alpha_composite(base_image, bar_graph)

    # Render text
    black = (0, 0, 0)
    white = (255, 255, 255)

    font = ImageFont.truetype('./assets/minecraft.ttf', 20)
    player_y = 33
    player_txt = "'s Most Played Modes"

    totallength = draw.textlength(name, font=font) + draw.textlength(player_txt, font=font)
    startpoint = (640 - totallength) / 2

    draw = ImageDraw.Draw(base_image)

    draw.text((startpoint + 2, player_y + 2), name, fill=black, font=font)
    draw.text((startpoint, player_y), name, fill=rankcolor, font=font)

    startpoint += draw.textlength(name, font=font)

    draw.text((startpoint + 2, player_y + 2), player_txt, fill=black, font=font)
    draw.text((startpoint, player_y), player_txt, fill=white, font=font)

    # Render the titles
    overlay_image = Image.open('./assets/bg/mostplayed/overlay.png')
    base_image = Image.alpha_composite(base_image, overlay_image)

    # Return the image
    image_bytes = BytesIO()
    base_image.save(image_bytes, format='PNG')
    image_bytes.seek(0)

    return image_bytes
