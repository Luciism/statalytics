from PIL import Image

import statalib as lib
from statalib import hypixel, to_thread
from statalib.render import ImageRender, RenderBackground


bg = RenderBackground(dir="hotbar")

SLOT_POSITIONS = [
    (40, 424), (130, 424), (220, 424), (310, 424),
    (400, 424), (490, 424), (580, 424), (670, 424), (760, 424)
]

@to_thread
def render_hotbar(
    name: str,
    uuid: str,
    hypixel_data: dict
) -> bytes:
    try:
        hypixel_data = hypixel_data['player']
        hotbar_layout = hypixel_data['stats']['Bedwars']['favorite_slots'].split(',')
    except (KeyError, TypeError):
        hotbar_layout = ['null'] * 9  # Hotbar not configured, use empty hotbar

    rank_info = hypixel.get_rank_info(hypixel_data)

    im = ImageRender(bg.load_background_image(uuid, {
        "level": 0, "rank_info": rank_info}))

    # Create a seperate composite image to paste the items onto.
    composite_image = Image.new("RGBA", im.size)

    for i, item in enumerate(hotbar_layout):
        item_image = lib.ASSET_LOADER.load_image(f"bg/hotbar/{item.lower()}.png")
        item_image = item_image.convert("RGBA")

        # Paste the item image onto the composite image.
        composite_image.paste(item_image, SLOT_POSITIONS[i], item_image)

    # Merge images
    im.overlay_image(composite_image)
    im.overlay_image(lib.ASSET_LOADER.load_image("bg/hotbar/overlay.png"))

    # Render name
    text = f"{rank_info['color']}{name}&f's Hotbar"

    im.text.draw(text, {
        "position": (440, 53),
        "font_size": 36,
        "shadow_offset": (4, 4),
        "align": "center"
    })

    return im.to_bytes()
