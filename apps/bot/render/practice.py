from calc.practice import PracticeStats
import statalib as lib
from statalib import to_thread
from statalib.render import (
    render_display_name,
    get_background,
    paste_skin,
    render_progress_bar,
    render_mc_text,
    image_to_bytes
)


@to_thread
def render_practice(
    name: str,
    uuid: str,
    hypixel_data: dict,
    skin_model: bytes
) -> bytes:
    stats = PracticeStats(hypixel_data)
    xp_bar_progress = stats.progress[2]

    image = get_background(
        bg_dir='practice', uuid=uuid, level=stats.level, rank_info=stats.rank_info
    ).convert("RGBA")

    data = [
        {'position': (87, 131), 'text': f'&a{stats.bridging_completed:,}'},
        {'position': (241, 131), 'text': f'&c{stats.bridging_failed:,}'},
        {'position': (378, 131), 'text': f'&6{stats.bridging_ratio:,}'},
        {'position': (87, 190), 'text': f'&a{stats.tnt_completed:,}'},
        {'position': (241, 190), 'text': f'&c{stats.tnt_failed:,}'},
        {'position': (378, 190), 'text': f'&6{stats.tnt_ratio:,}'},
        {'position': (87, 249), 'text': f'&a{stats.mlg_completed:,}'},
        {'position': (241, 249), 'text': f'&c{stats.mlg_failed:,}'},
        {'position': (378, 249), 'text': f'&6{stats.mlg_ratio:,}'},
        {'position': (87, 308), 'text': f'&a{stats.pearl_completed:,}'},
        {'position': (241, 308), 'text': f'&c{stats.pearl_failed:,}'},
        {'position': (378, 308), 'text': f'&6{stats.pearl_ratio:,}'},
        {'position': (88, 368), 'text': f'&d{stats.straight_short_record}'},
        {'position': (242, 368), 'text': f'&d{stats.straight_medium_record}'},
        {'position': (397, 368), 'text': f'&d{stats.straight_long_record}'},
        {'position': (553, 368), 'text': f'&d{stats.straight_average_time}'},
        {'position': (88, 426), 'text': f'&d{stats.diagonal_short_record}'},
        {'position': (242, 426), 'text': f'&d{stats.diagonal_medium_record}'},
        {'position': (397, 426), 'text': f'&d{stats.diagonal_long_record}'},
        {'position': (553, 426), 'text': f'&d{stats.diagonal_average_time}'},
        {'position': (537, 249), 'text': f'&d{stats.total_attempts:,}'},
        {'position': (537, 308), 'text': f'&d{stats.blocks_placed:,}'},
        {'position': (537, 46), 'text':'(Overall)'}
    ]

    for values in data:
        render_mc_text(
            image=image,
            shadow_offset=(2, 2),
            font=lib.ASSET_LOADER.load_font("main.ttf", 16),
            align='center',
            **values
        )

    render_display_name(
        username=name,
        rank_info=stats.rank_info,
        image=image,
        font_size=22,
        position=(226, 30),
        align='center'
    )

    render_progress_bar(
        level=stats.level,
        xp_bar_progress=xp_bar_progress,
        position=(226, 61),
        image=image,
        align='center'
    )

    paste_skin(skin_model, image, positions=(466, 69))

    # Paste overlay
    overlay_image = lib.ASSET_LOADER.load_image("bg/practice/overlay.png")
    overlay_image = overlay_image.convert("RGBA")
    image.paste(overlay_image, (0, 0), overlay_image)

    return image_to_bytes(image)
