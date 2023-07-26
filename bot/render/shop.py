import os

from PIL import Image, ImageFont

from statalib import get_rank_info, to_thread
from statalib.render import (
    get_background,
    render_mc_text,
    image_to_bytes
)


@to_thread
def render_shop(
    name: str,
    uuid: str,
    hypixel_data: dict
):
    # Get shop layout and positions
    slots = [
        (40, 80), (130, 80), (220, 80), (310, 80), (400, 80), (490, 80),
        (580, 80), (40, 170), (130, 170), (220, 170), (310, 170),
        (400, 170), (490, 170), (580, 170), (40, 260), (130, 260),
        (220, 260), (310, 260), (400, 260), (490, 260), (580, 260)
    ]

    try:
        shop = hypixel_data['player']['stats']['Bedwars']['favourites_2'].split(',')
    except (KeyError, TypeError):
        # Default shop layout
        shop = ['wool', 'stone_sword', 'chainmail_boots', 'null',
                'bow', 'speed_ii_potion_(45_seconds)', 'tnt', 'oak_wood_planks',
                'iron_sword', 'iron_boots', 'shears', 'arrow',
                'jump_v_potion_(45_seconds)', 'water_bucket'] + ['null'] * 7

    rank_info = get_rank_info(hypixel_data=hypixel_data['player'])

    base_image = get_background(
        path='./assets/bg/shop', uuid=uuid,
        default='base', level=0, rank_info=rank_info
    ).convert("RGBA")

    composite_image = Image.new("RGBA", base_image.size)

    for i, item in enumerate(shop):
        if os.path.exists(f"./assets/bg/shop/{item}.png"):
            top_image = Image.open(f"./assets/bg/shop/{item}.png")
        else:
            top_image = Image.open("./assets/bg/shop/rotational_item.png")

        top_image = top_image.convert("RGBA")
        composite_image.paste(top_image, slots[i], top_image)

    font = ImageFont.truetype('./assets/fonts/minecraft.ttf', 32)

    # If the name box is transparent, color the name, otherwise default gray
    name_backdrop_alpha = base_image.getpixel((49, 25))[3]
    if name_backdrop_alpha == 76:
        render_mc_text(
            text=f"&f{name}'s Quick Buy",
            position=(350, 29),
            font=font,
            image=base_image,
            shadow_offset=(2, 2),
            align='center'
        )
    else:
        render_mc_text(
            text=f"&8{name}'s Quick Buy",
            position=(42, 29),
            font=font,
            image=base_image,
        )

    base_image = Image.alpha_composite(base_image, composite_image)

    return image_to_bytes(base_image)
