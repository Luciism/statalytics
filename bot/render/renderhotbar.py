import os
import json
import random
from io import BytesIO
import requests
from PIL import Image, ImageFont, ImageDraw
from helper.custombackground import background
from helper.rendername import get_rank_color

def renderhotbar(name, uuid):
    # Get api key
    with open('./database/apikeys.json', 'r') as datafile:
        allkeys = json.load(datafile)['keys']
    key = random.choice(list(allkeys))

    # Get shop layout and positions
    slots = [(40, 424), (130, 424), (220, 424), (310, 424), (400, 424), (490, 424), (580, 424), (670, 424), (760, 424)]
    response = requests.get(f"https://api.hypixel.net/player?key={allkeys[key]}&uuid={uuid}", timeout=10)
    try:
        hypixel_data = response.json()['player']
        hotbar = hypixel_data['stats']['Bedwars']['favorite_slots'].split(',')
    except KeyError:
        return False

    # Open the base image
    image_location = background(path='./assets/hotbar', uuid=uuid, default='hotbar')
    base_image = Image.open(image_location)
    base_image = base_image.convert("RGBA")

    i = 0
    for i, item in enumerate(hotbar):
        # Open the top image (with transparency)
        top_image = Image.open(f"./assets/hotbar/{item.lower()}.png")

        # Color compatible
        top_image = top_image.convert("RGBA")

        # Paste the top image onto the base image at the specified position
        base_image.paste(top_image, slots[i], top_image)

    overlay_image = Image.open('./assets/hotbar/hotbar_overlay.png')
    overlay_image = overlay_image.convert("RGBA")

    base_image.paste(overlay_image, (0, 0), overlay_image)

    # Render name
    player_rank_info = {
        'rank': hypixel_data.get('rank', 'NONE') if name != "Technoblade" else "TECHNO",
        'packageRank': hypixel_data.get('packageRank', 'NONE'),
        'newPackageRank': hypixel_data.get('newPackageRank', 'NONE'),
        'monthlyPackageRank': hypixel_data.get('monthlyPackageRank', 'NONE'),
        'rankPlusColor': hypixel_data.get('rankPlusColor', None) if name != "Technoblade" else "AQUA"
    }

    rankcolor = get_rank_color(player_rank_info)

    black = (0, 0, 0)
    white = (255, 255, 255)

    font = ImageFont.truetype('./assets/minecraft.ttf', 36)
    player_y = 53
    player_txt = "'s Hotbar"

    draw = ImageDraw.Draw(base_image)

    totallength = draw.textlength(name, font=font) + draw.textlength(player_txt, font=font)
    startpoint = (base_image.width - totallength) / 2

    draw.text((startpoint + 4, player_y + 4), name, fill=black, font=font)
    draw.text((startpoint, player_y), name, fill=rankcolor, font=font)

    startpoint += draw.textlength(name, font=font)

    draw.text((startpoint + 4, player_y + 4), player_txt, fill=black, font=font)
    draw.text((startpoint, player_y), player_txt, fill=white, font=font)

    # Return the result
    image_bytes = BytesIO()
    base_image.save(image_bytes, format='PNG')
    image_bytes.seek(0)

    return image_bytes
