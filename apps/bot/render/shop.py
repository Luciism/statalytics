from PIL import Image

import statalib as lib
from statalib import hypixel, to_thread
from statalib.render import ImageRender, BackgroundImageLoader


bg = BackgroundImageLoader(dir="shop")

SLOT_POSITIONS = [
    (40, 80), (130, 80), (220, 80), (310, 80), (400, 80), (490, 80),
    (580, 80), (40, 170), (130, 170), (220, 170), (310, 170),
    (400, 170), (490, 170), (580, 170), (40, 260), (130, 260),
    (220, 260), (310, 260), (400, 260), (490, 260), (580, 260)
]

DEFAULT_SHOP_LAYOUT = [
    'wool', 'stone_sword', 'chainmail_boots', 'null',
    'bow', 'speed_ii_potion_(45_seconds)', 'tnt', 'oak_wood_planks',
    'iron_sword', 'iron_boots', 'shears', 'arrow',
    'jump_v_potion_(45_seconds)', 'water_bucket'
] + (['null'] * 7)

def get_shop_layout(hypixel_data: dict) -> list:
    try:
        return hypixel_data['player']['stats']['Bedwars']['favourites_2'].split(',')
    except (KeyError, TypeError):
        return DEFAULT_SHOP_LAYOUT

@to_thread
def render_shop(
    name: str,
    uuid: str,
    hypixel_data: dict
) -> bytes:
    rank_info = hypixel.get_rank_info(hypixel_player_data=hypixel.get_player_dict(hypixel_data))

    im = ImageRender(bg.load_background_image(uuid, {
        "level": 0, "rank_info": rank_info}))

    composite_image = Image.new("RGBA", im.size)
    shop_layout = get_shop_layout(hypixel_data)

    for i, item in enumerate(shop_layout):
        if lib.ASSET_LOADER.image_file_exists(f"bg/shop/{item}.png"):
            top_image = lib.ASSET_LOADER.load_image(f"bg/shop/{item}.png")
        else:
            top_image = lib.ASSET_LOADER.load_image("bg/shop/rotational_item.png")

        top_image = top_image.convert("RGBA")
        composite_image.paste(top_image, SLOT_POSITIONS[i], top_image)

    # If the name box is transparent, color the name, otherwise default gray
    name_backdrop_alpha = im._image.getpixel((49, 25))[3]
    if name_backdrop_alpha == 76:
        im.text.draw(f"&f{name}'s Quick Buy", {
            "position": (350, 29),
            "font_size": 32,
            "shadow_offset": (2, 2),
            "align": "center"
        })
    else:
        im.text.draw(f"&8{name}'s Quick Buy", {
            "position": (42, 29),
            "font_size": 32,
            "align": "left"
        })

    im.overlay_image(composite_image)

    return im.to_bytes()
