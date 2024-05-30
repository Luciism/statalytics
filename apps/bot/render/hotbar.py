from PIL import Image

import statalib as lib
from statalib import get_rank_info, to_thread
from statalib.render import (
    get_background,
    get_rank_color,
    render_mc_text,
    image_to_bytes
)


@to_thread
def render_hotbar(
    name: str,
    uuid: str,
    hypixel_data: dict
) -> bytes:
    slots = [(40, 424), (130, 424), (220, 424), (310, 424),
             (400, 424), (490, 424), (580, 424), (670, 424), (760, 424)]

    try:
        hypixel_data = hypixel_data['player']
        hotbar = hypixel_data['stats']['Bedwars']['favorite_slots'].split(',')
    except (KeyError, TypeError):
        hotbar = ['null'] * 9  # Hotbar not configured, use empty hotbar

    rank_info = get_rank_info(hypixel_data)
    rank_color_code = get_rank_color(rank_info)

    base_image = get_background(
        bg_dir='hotbar', uuid=uuid, level=0, rank_info=rank_info
    ).convert("RGBA")

    composite_image = Image.new("RGBA", base_image.size)

    for i, item in enumerate(hotbar):
        top_image = lib.ASSET_LOADER.load_image(f"bg/hotbar/{item.lower()}.png")
        top_image = top_image.convert("RGBA")

        composite_image.paste(top_image, slots[i], top_image)

    # Paste overlay image
    overlay_image = lib.ASSET_LOADER.load_image("bg/hotbar/overlay.png")
    overlay_image = overlay_image.convert("RGBA")
    composite_image.paste(overlay_image, (0, 0), overlay_image)

    # Merge images
    base_image = Image.alpha_composite(base_image, composite_image)

    # Render name
    text = f"{rank_color_code}{name}&f's Hotbar"

    render_mc_text(
        text=text,
        position=(440, 53),
        font=lib.ASSET_LOADER.load_font("main.ttf", 36),
        image=base_image,
        shadow_offset=(4, 4),
        align='center'
    )

    return image_to_bytes(base_image)
