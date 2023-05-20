import os

from io import BytesIO
from PIL import Image, ImageDraw, ImageFont
from helper.custombackground import background

def render_shop(uuid, hypixel_data):
    # Get shop layout and positions
    slots = [(40, 80), (130, 80), (220, 80), (310, 80), (400, 80), (490, 80), (580, 80), (40, 170), (130, 170), (220, 170), (310, 170),
             (400, 170), (490, 170), (580, 170), (40, 260), (130, 260), (220, 260), (310, 260), (400, 260), (490, 260), (580, 260)]

    try: shop = hypixel_data['player']['stats']['Bedwars']['favourites_2'].split(',')
    except KeyError: return False

    # Open the base image
    image_location = background(path='./assets/shop', uuid=uuid, default='base')
    base_image = Image.open(image_location)
    base_image = base_image.convert("RGBA")

    for i, item in enumerate(shop):
        if os.path.exists(f"./assets/shop/{item}.png"):
            top_image = Image.open(f"./assets/shop/{item}.png")
        else:
            top_image = Image.open(f"./assets/shop/rotational_item.png")
        top_image = top_image.convert("RGBA")
        base_image.paste(top_image, slots[i], top_image)

    draw = ImageDraw.Draw(base_image)
    font = ImageFont.truetype('./assets/minecraft.ttf', 32)

    name = hypixel_data['player']['displayname']
    draw.text((42, 29), f"{name}'s Quick Buy", fill=(80, 80, 80), font=font)

    # Return the result
    image_bytes = BytesIO()
    base_image.save(image_bytes, format='PNG')
    image_bytes.seek(0)

    return image_bytes
