from io import BytesIO
from PIL import Image, ImageDraw, ImageFont
from helper.rendername import render_level_and_name
from calc.cosmetics import ActiveCosmetics
from helper.rendertools import get_background

def render_cosmetics(name, uuid, hypixel_data):
    cosmetics = ActiveCosmetics(name, hypixel_data)
    level = cosmetics.level
    player_rank_info = cosmetics.player_rank_info

    cosmetic_data = {
        'shopkeeper_skin': (299, 100),
        'projectile_trail': (299, 133),
        'death_cry': (299, 166),
        'wood_skin': (299, 199),
        'kill_effect': (299, 232),
        'island_topper': (299, 265),
        'victory_dance': (299, 298),
        'glyph': (299, 331),
        'spray': (299, 364),
        'bed_destroy': (299, 397),
        'kill_message': (299, 430)
    }

    image = get_background(path='./assets/cosmetics', uuid=uuid,
                           default='base', level=level, rank_info=player_rank_info)

    image = image.convert("RGBA")

    draw = ImageDraw.Draw(image)
    font = ImageFont.truetype('./assets/minecraft.ttf', 16)

    white = (255, 255, 255)
    black = (0, 0, 0)

    for cosmetic, (x, y) in cosmetic_data.items():
        cosmetic_text = getattr(cosmetics, cosmetic)
        draw.text((x + 2, y + 2), cosmetic_text, fill=black, font=font)
        draw.text((x, y), cosmetic_text, fill=white, font=font)

    # Render the titles
    title_image = Image.open('./assets/cosmetics/overlay.png')
    image.paste(title_image, (0, 0), title_image)

    # Render player name
    render_level_and_name(name, level, player_rank_info, image,
                          box_positions=(121, 398), position_y=51, fontsize=20)

    # Return the image
    image_bytes = BytesIO()
    image.save(image_bytes, format='PNG')
    image_bytes.seek(0)

    return image_bytes
