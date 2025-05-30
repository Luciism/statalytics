from calc.cosmetics import ActiveCosmetics
import statalib as lib
from statalib import to_thread
from statalib.render import ImageRender, BackgroundImageLoader


bg = BackgroundImageLoader(dir="cosmetics")

@to_thread
def render_cosmetics(
    name: str,
    uuid: str,
    hypixel_data: lib.HypixelData 
) -> bytes:
    cosmetics = ActiveCosmetics(name, hypixel_data)
    level = cosmetics.level
    rank_info = cosmetics.rank_info

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

    im = ImageRender(bg.load_background_image(
        uuid, {"level": level, "rank_info": rank_info}))

    for cosmetic, (x, y) in cosmetic_data.items():
        text: str = getattr(cosmetics, cosmetic)

        im.text.draw(text, {
            "position": (x, y),
            "font_size": 16,
            "shadow_offset": (2, 2)
        })

    im.player.render_hypixel_username(
        name, rank_info, text_options={
        "align": "center",
        "font_size": 20,
        "position": (320, 51)
    })

    # Render the overlay image
    im.overlay_image(lib.ASSET_LOADER.load_image("bg/cosmetics/overlay.png"))

    return im.to_bytes()
