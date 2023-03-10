import os
from io import BytesIO
from PIL import Image, ImageDraw, ImageFont
from rendername import render_name
from calccosmetics import ActiveCosmetics
from custombackground import background

def rendercosmetics(name, uuid):
    image_location = background(path=f'{os.getcwd()}/assets/cosmetics', uuid=uuid, default='activecosmetics')
    image = Image.open(image_location)
    image = image.convert("RGBA")

    draw = ImageDraw.Draw(image)

    font = ImageFont.truetype(f'{os.getcwd()}/assets/minecraft.ttf', 16)

    white = (255, 255, 255)
    black = (0, 0, 0)

    cosmetics = ActiveCosmetics(name, uuid)
    level = cosmetics.level
    playerrank = cosmetics.get_player_rank()

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

    # Render the cosmetics
    for cosmetic, (x, y) in cosmetic_data.items():
        cosmetic_text = getattr(cosmetics, cosmetic)
        draw.text((x + 2, y + 2), cosmetic_text, fill=black, font=font)
        draw.text((x, y), cosmetic_text, fill=white, font=font)

    # Render the titles
    title_image = Image.open(f'{os.getcwd()}/assets/cosmetics/activecosmetics_titles.png')
    image.paste(title_image, (0, 0), title_image)

    # Render player name
    render_name(name, level, playerrank, image, 51, fontsize=20)

    # Return the image
    image_bytes = BytesIO()
    image.save(image_bytes, format='PNG')
    image_bytes.seek(0)

    return image_bytes
