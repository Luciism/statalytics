import os
import json
import random
from io import BytesIO
import requests
from PIL import Image
from helper.custombackground import background

def rendershop(uuid):
    # Get api key
    with open('./database/apikeys.json', 'r') as datafile:
        allkeys = json.load(datafile)['keys']
    key = random.choice(list(allkeys))

    # Get shop layout and positions
    slots = [(40, 80), (130, 80), (220, 80), (310, 80), (400, 80), (490, 80), (580, 80), (40, 170), (130, 170), (220, 170), (310, 170), (400, 170), (490, 170), (580, 170), (40, 260), (130, 260), (220, 260), (310, 260), (400, 260), (490, 260), (580, 260)]
    response = requests.get(f"https://api.hypixel.net/player?key={allkeys[key]}&uuid={uuid}", timeout=10)
    try:
        shop = response.json()['player']['stats']['Bedwars']['favourites_2'].split(',')
    except Exception:
        return False

    # Open the base image
    image_location = background(path='./assets/shop', uuid=uuid, default='base')
    base_image = Image.open(image_location)
    base_image = base_image.convert("RGBA")

    i = 0
    for item in shop:
        # Open the top image (with transparency)
        top_image = Image.open(f"{os.getcwd()}/assets/shop/{item}.png")

        # Color compatible
        top_image = top_image.convert("RGBA")

        # Paste the top image onto the base image at the specified position
        base_image.paste(top_image, slots[i], top_image)
        i += 1

    # Return the result
    image_bytes = BytesIO()
    base_image.save(image_bytes, format='PNG')
    image_bytes.seek(0)

    return image_bytes
