from PIL import Image, ImageDraw, ImageFont

from statalib import get_rank_info, to_thread, get_player_dict, REL_PATH
from statalib.render import (
    get_background,
    get_rank_color,
    image_to_bytes,
    render_mc_text
)


@to_thread
def render_mostplayed(
    name: str,
    uuid: str,
    hypixel_data: dict
) -> bytes:
    hypixel_data = get_player_dict(hypixel_data)
    bedwars_data: dict = hypixel_data.get('stats', {}).get('Bedwars', {})

    solos = bedwars_data.get('eight_one_games_played_bedwars', 1)
    doubles = bedwars_data.get('eight_two_games_played_bedwars', 1)
    threes = bedwars_data.get('four_three_games_played_bedwars', 1)
    fours = bedwars_data.get('four_four_games_played_bedwars', 1)

    rank_info = get_rank_info(hypixel_data)
    rank_color_code = get_rank_color(rank_info)

    # Get ratio
    numbers = [int(solos), int(doubles), int(threes), int(fours)]
    total = sum(numbers)
    ratios = [num / total for num in numbers]

    color = (45, 45, 255, 127)

    # Define the coordinates for the bars
    positions = [(97, 354), (220, 354), (343, 354), (466, 354)]

    # Open Images
    base_image = get_background(
        bg_dir='mostplayed', uuid=uuid, level=0, rank_info=rank_info
    ).convert("RGBA")

    bar_plot_img = Image.new('RGBA', (640, 420), (0, 0, 0, 0))
    draw = ImageDraw.Draw(bar_plot_img)

    # Ensure the bars are under 500 pixels in height and still relative
    if max(ratios) * 500 > 250:
        difference = (max(ratios) * 500) - 250
        ratios = [value - (difference / 500)
                  if value - (difference / 500) > 0 else 0 for value in ratios]

    # Draw the bars
    for i, value in enumerate(ratios):
        height = 250 if value * 500 > 250 else value * 500

        top_left = (positions[i][0], positions[i][1] - height)
        bottom_right = (positions[i][0] + 77, positions[i][1])
        draw.rectangle((top_left, bottom_right), fill=color)

    base_image = Image.alpha_composite(base_image, bar_plot_img)

    font = ImageFont.truetype(f'{REL_PATH}/assets/fonts/minecraft.ttf', 20)
    text = f"{rank_color_code}{name}&f's Most Played Modes"

    render_mc_text(
        text=text,
        position=(320, 33),
        font=font,
        image=base_image,
        shadow_offset=(4, 4),
        align='center'
    )

    # Paste the overlay image
    overlay_image = Image.open(f'{REL_PATH}/assets/bg/mostplayed/overlay.png')
    base_image = Image.alpha_composite(base_image, overlay_image)

    return image_to_bytes(base_image)
