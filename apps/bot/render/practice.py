from calc.practice import PracticeStats
import statalib as lib
from statalib import to_thread
from statalib.render import ImageRender, BackgroundImageLoader


bg = BackgroundImageLoader(dir="practice")

@to_thread
def render_practice(
    name: str,
    uuid: str,
    hypixel_data: dict,
    skin_model: bytes
) -> bytes:
    stats = PracticeStats(hypixel_data)

    im = ImageRender(bg.load_background_image(uuid, {
        "level": stats.level, "rank_info": stats.rank_info}))

    im.text.draw_many([
        (f'&a{stats.bridging_completed:,}', {'position': (87, 131)}),
        (f'&c{stats.bridging_failed:,}', {'position': (241, 131)}),
        (f'&6{stats.bridging_ratio:,}', {'position': (378, 131)}),
        (f'&a{stats.tnt_completed:,}', {'position': (87, 190)}),
        (f'&c{stats.tnt_failed:,}', {'position': (241, 190)}),
        (f'&6{stats.tnt_ratio:,}', {'position': (378, 190)}),
        (f'&a{stats.mlg_completed:,}', {'position': (87, 249)}),
        (f'&c{stats.mlg_failed:,}', {'position': (241, 249)}),
        (f'&6{stats.mlg_ratio:,}', {'position': (378, 249)}),
        (f'&a{stats.pearl_completed:,}', {'position': (87, 308)}),
        (f'&c{stats.pearl_failed:,}', {'position': (241, 308)}),
        (f'&6{stats.pearl_ratio:,}', {'position': (378, 308)}),
        (f'&d{stats.straight_short_record}', {'position': (88, 368)}),
        (f'&d{stats.straight_medium_record}', {'position': (242, 368)}),
        (f'&d{stats.straight_long_record}', {'position': (397, 368)}),
        (f'&d{stats.straight_average_time}', {'position': (553, 368)}),
        (f'&d{stats.diagonal_short_record}', {'position': (88, 426)}),
        (f'&d{stats.diagonal_medium_record}', {'position': (242, 426)}),
        (f'&d{stats.diagonal_long_record}', {'position': (397, 426)}),
        (f'&d{stats.diagonal_average_time}', {'position': (553, 426)}),
        (f'&d{stats.total_attempts:,}', {'position': (537, 249)}),
        (f'&d{stats.blocks_placed:,}', {'position': (537, 308)}),
        ('(Overall)', {'position': (537, 46)}),
    ], default_text_options={
        "shadow_offset": (2, 2), "align": "center", "font_size": 16
    })

    im.player.render_hypixel_username(
        name, stats.rank_info, text_options={
        "align": "center",
        "font_size": 22,
        "position": (226, 30)
    })

    im.progress.draw_progress_bar(
        stats.level,
        progress_percentage=stats.leveling.progression.progress_percent,
        position=(226, 61),
        align="center"
    )

    im.player.paste_skin(skin_model, position=(466, 69))

    # Paste overlay
    im.overlay_image(lib.ASSET_LOADER.load_image("bg/practice/overlay.png"))

    return im.to_bytes()
