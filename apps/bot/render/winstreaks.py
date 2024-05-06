from calc.winstreaks import WinstreakStats
import statalib as lib
from statalib import to_thread
from statalib.render import (
    render_display_name,
    get_background,
    paste_skin,
    render_progress_bar,
    render_progress_text,
    render_mc_text,
    image_to_bytes
)


@to_thread
def render_winstreaks(
    name: str,
    uuid: str,
    hypixel_data: dict,
    skin_model: bytes
):
    stats = WinstreakStats(hypixel_data)

    level = stats.level
    rank_info = stats.rank_info

    progress, target, xp_bar_progress = stats.progress

    image = get_background(
        bg_dir='winstreaks', uuid=uuid, level=level, rank_info=rank_info
    ).convert("RGBA")

    # Render the stat values
    data = [
        {'position': (118, 190), 'text': f'&a{stats.winstreak_overall}'},
        {'position': (333, 190), 'text': f'&a{stats.winstreak_solos}'},
        {'position': (118, 249), 'text': f'&a{stats.winstreak_doubles}'},
        {'position': (333, 249), 'text': f'&a{stats.winstreak_threes}'},
        {'position': (118, 308), 'text': f'&a{stats.winstreak_fours}'},
        {'position': (333, 308), 'text': f'&a{stats.winstreak_4v4}'},
        {'position': (537, 249), 'text': f'&d{stats.wins:,}'},
        {'position': (537, 308), 'text': f'&d{stats.api_status}'}
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
        position=(226, 31),
        align='center'
    )

    render_progress_bar(
        level=stats.level,
        xp_bar_progress=xp_bar_progress,
        position=(226, 91),
        image=image,
        align='center'
    )

    render_progress_text(
        progress=progress,
        target=target,
        position=(226, 122),
        image=image,
        align='center'
    )

    paste_skin(skin_model, image, positions=(466, 69))

    overlay_image = lib.ASSET_LOADER.load_image("bg/winstreaks/overlay.png")
    overlay_image = overlay_image.convert("RGBA")
    image.paste(overlay_image, (0, 0), overlay_image)

    return image_to_bytes(image)
