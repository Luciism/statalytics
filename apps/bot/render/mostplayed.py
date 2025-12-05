from PIL import Image, ImageDraw

import statalib as lib
from statalib import HypixelData, hypixel, to_thread
from statalib.render import ImageRender, BackgroundImageLoader


bg = BackgroundImageLoader(dir="mostplayed")

BAR_COLOR = (45, 45, 255, 127)
BAR_POSITIONS = [(97, 354), (220, 354), (343, 354), (466, 354)]
MAX_BAR_HEIGHT = 250 

@to_thread
def render_mostplayed(
    name: str,
    uuid: str,
    hypixel_data: HypixelData 
) -> bytes:
    hypixel_data = hypixel.get_player_dict(hypixel_data)
    bedwars_data: dict = hypixel_data.get('stats', {}).get('Bedwars', {})

    solos: int = bedwars_data.get('eight_one_games_played_bedwars', 0)
    doubles: int = bedwars_data.get('eight_two_games_played_bedwars', 0)
    threes: int = bedwars_data.get('four_three_games_played_bedwars', 0)
    fours: int = bedwars_data.get('four_four_games_played_bedwars', 0)

    rank_info = hypixel.get_rank_info(hypixel_data)

    # Get ratio
    values: list[int] = [solos, doubles, threes, fours]
    normal = 1 / sum(values)

    heights = [normal * value * MAX_BAR_HEIGHT for value in values]

    # Make sure highest bar always reaches top
    height_multiplier = MAX_BAR_HEIGHT / max(heights)

    # Open Images
    im = ImageRender(bg.load_background_image(uuid, {
        "level": 0, "rank_info": rank_info}))

    bar_plot_img = Image.new('RGBA', (640, 420), (0, 0, 0, 0))
    draw = ImageDraw.Draw(bar_plot_img)


    # Draw the bars
    for i, height in enumerate(heights):
        top_left = (BAR_POSITIONS[i][0], BAR_POSITIONS[i][1] - height * height_multiplier)
        bottom_right = (BAR_POSITIONS[i][0] + 77, BAR_POSITIONS[i][1])
        draw.rectangle((top_left, bottom_right), fill=BAR_COLOR)

    im.overlay_image(bar_plot_img)

    text = f"{rank_info['color']}{name}&f's Most Played Modes"

    im.text.draw(text, {
        "position": (320, 33),
        "font_size": 20,
        "shadow_offset": (4, 4),
        "align": "center"
    })

    # Paste the overlay image
    im.overlay_image(lib.ASSET_LOADER.load_image("bg/mostplayed/overlay.png"))

    return im.to_bytes()
