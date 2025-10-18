from PIL import Image

import statalib as lib
from statalib import HypixelData, HypixelPlayerData, hypixel, to_thread
from statalib.render import ImageRender, BackgroundImageLoader


bg = BackgroundImageLoader(dir="quickbuy")

SLOT_SIZE = 90

DEFAULT_SHOP_LAYOUT = [
    'wool', 'stone_sword', 'chainmail_boots', 'null',
    'bow', 'speed_ii_potion_(45_seconds)', 'tnt', 'oak_wood_planks',
    'iron_sword', 'iron_boots', 'shears', 'arrow',
    'jump_v_potion_(45_seconds)', 'water_bucket'
] + (['null'] * 7)

def get_quickbuy_menu_layout(hypixel_data: HypixelPlayerData) -> list[str]:
    try:
        return hypixel_data['stats']['Bedwars']['favourites_2'].split(',')
    except (KeyError, TypeError):
        return DEFAULT_SHOP_LAYOUT

def get_hotbar_layout(hypixel_data: HypixelPlayerData) -> list[str]:
    try:
        return hypixel_data['stats']['Bedwars']['favorite_slots'].split(',')
    except (KeyError, TypeError):
        return ['null'] * 9  # Hotbar not configured, use empty hotbar


def draw_item_grid(
    size: tuple[int, int],
    item_list: list[str],
    base_path: str,
    default: str="null.png"
) -> Image.Image:
    composite_image = Image.new("RGBA", (SLOT_SIZE * size[0], SLOT_SIZE * size[1]))

    for i, item in enumerate(item_list):
        item = item.lower()

        x = (i % size[0]) * SLOT_SIZE
        y = (i // size[0]) * SLOT_SIZE

        if lib.ASSET_LOADER.image_file_exists(f"{base_path}/{item}.png"):
            top_image = lib.ASSET_LOADER.load_image(f"{base_path}/{item}.png")
        else:
            top_image = lib.ASSET_LOADER.load_image(f"{base_path}/{default}")

        top_image = top_image.convert("RGBA")
        composite_image.paste(top_image, (x, y), top_image)

    return composite_image


@to_thread
def render_quickbuy(
    name: str,
    uuid: str,
    hypixel_data: HypixelData,
    skin_model: bytes
) -> bytes:
    hypixel_player_data = hypixel.get_player_dict(hypixel_data)
    rank_info = hypixel.get_rank_info(hypixel_player_data)

    im = ImageRender(bg.load_background_image(uuid, {
        "level": 0, "rank_info": rank_info}))

    im.text.draw(f"{rank_info['formatted_prefix']}{name}&f's QuickBuy", {
        "position": (440, 67 - 16),
        "font_size": 32,
        "align": "center",
        "shadow_offset": (4, 4)
    })

    quickbuy_favourites = draw_item_grid(
        size=(7, 3),
        item_list=get_quickbuy_menu_layout(hypixel_player_data),
        base_path="bg/quickbuy/items",
        default="rotational_item.png"
    )
    im.overlay_image(quickbuy_favourites, source=(215, 119))

    hotbar_favourites = draw_item_grid(
        size=(9, 1),
        item_list=get_hotbar_layout(hypixel_player_data),
        base_path="bg/quickbuy/items/hotbar",
        default="null.png"
    )
    im.overlay_image(hotbar_favourites, source=(35, 409))

    im.player.paste_skin(skin_model, position=(47, 131))

    return im.to_bytes()

