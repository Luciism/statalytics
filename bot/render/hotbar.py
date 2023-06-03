from io import BytesIO
from PIL import Image, ImageFont, ImageDraw
from helper.rendertools import get_background, get_rank_color
from helper.calctools import get_player_rank_info

def render_hotbar(name, uuid, hypixel_data):
    slots = [(40, 424), (130, 424), (220, 424), (310, 424),
             (400, 424), (490, 424), (580, 424), (670, 424), (760, 424)]

    try:
        hypixel_data = hypixel_data['player']
        hotbar = hypixel_data['stats']['Bedwars']['favorite_slots'].split(',')
    except KeyError:
        hotbar = ['null'] * 9

    player_rank_info = get_player_rank_info(hypixel_data)
    rankcolor = get_rank_color(player_rank_info)

    base_image = get_background(path='./assets/hotbar', uuid=uuid,
                                default='base', level=0, rank_info=player_rank_info)

    base_image = base_image.convert("RGBA")

    composite_image = Image.new("RGBA", base_image.size)

    for i, item in enumerate(hotbar):
        top_image = Image.open(f"./assets/hotbar/{item.lower()}.png")
        top_image = top_image.convert("RGBA")
        composite_image.paste(top_image, slots[i], top_image)

    overlay_image = Image.open('./assets/hotbar/overlay.png')
    overlay_image = overlay_image.convert("RGBA")
    composite_image.paste(overlay_image, (0, 0), overlay_image)

    # Render name
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

    base_image = Image.alpha_composite(base_image, composite_image)

    # Return the result
    image_bytes = BytesIO()
    base_image.save(image_bytes, format='PNG')
    image_bytes.seek(0)

    return image_bytes
