from PIL import Image, ImageFont

from calc.practice import Practice
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
    skin_res: bytes
) -> bytes:
    practice = Practice(hypixel_data)

    level = practice.level
    rank_info = practice.rank_info
    progress_of_10 = practice.progress[2]

    bridge_completed, bridge_failed, bridge_ratio = practice.get_bridging_stats()
    pearl_completed, pearl_failed, pearl_ratio = practice.get_pearl_stats()
    tnt_completed, tnt_failed, tnt_ratio = practice.get_tnt_stats()
    mlg_completed, mlg_failed, mlg_ratio = practice.get_mlg_stats()

    strt_short, strt_medium, strt_long, strt_avg = practice.get_straight_times()
    diag_short, diag_medium, diag_long, diag_avg = practice.get_diagonal_times()
    blocks_placed = practice.get_blocks_placed()

    attempts = practice.get_attempts()

    image = get_background(
        path='./assets/bg/practice', uuid=uuid,
        default='base', level=level, rank_info=rank_info
    ).convert("RGBA")

    minecraft_16 = ImageFont.truetype('./assets/fonts/minecraft.ttf', 16)

    # Render the stat values
    data = [
        {'position': (87, 131), 'text': f'&a{bridge_completed}'},
        {'position': (241, 131), 'text': f'&c{bridge_failed}'},
        {'position': (378, 131), 'text': f'&6{bridge_ratio}'},
        {'position': (87, 190), 'text': f'&a{tnt_completed}'},
        {'position': (241, 190), 'text': f'&c{tnt_failed}'},
        {'position': (378, 190), 'text': f'&6{tnt_ratio}'},
        {'position': (87, 249), 'text': f'&a{mlg_completed}'},
        {'position': (241, 249), 'text': f'&c{mlg_failed}'},
        {'position': (378, 249), 'text': f'&6{mlg_ratio}'},
        {'position': (87, 308), 'text': f'&a{pearl_completed}'},
        {'position': (241, 308), 'text': f'&c{pearl_failed}'},
        {'position': (378, 308), 'text': f'&6{pearl_ratio}'},
        {'position': (88, 368), 'text': f'&d{strt_short}'},
        {'position': (242, 368), 'text': f'&d{strt_medium}'},
        {'position': (397, 368), 'text': f'&d{strt_long}'},
        {'position': (553, 368), 'text': f'&d{strt_avg}'},
        {'position': (88, 426), 'text': f'&d{diag_short}'},
        {'position': (242, 426), 'text': f'&d{diag_medium}'},
        {'position': (397, 426), 'text': f'&d{diag_long}'},
        {'position': (553, 426), 'text': f'&d{diag_avg}'},
        {'position': (537, 249), 'text': f'&d{attempts}'},
        {'position': (537, 308), 'text': f'&d{blocks_placed}'},
        {'position': (537, 46), 'text':'(Overall)'}
    ]

    for values in data:
        render_mc_text(
            image=image,
            shadow_offset=(2, 2),
            font=minecraft_16,
            align='center',
            **values
        )

    render_display_name(
        username=name,
        rank_info=rank_info,
        image=image,
        font_size=22,
        position=(226, 30),
        align='center'
    )

    render_progress_bar(
        level=level,
        progress_of_10=progress_of_10,
        position=(226, 61),
        image=image,
        align='center'
    )

    paste_skin(skin_res, image, positions=(466, 69))

    # Paste overlay
    overlay_image = Image.open('./assets/bg/practice/overlay.png')
    overlay_image = overlay_image.convert("RGBA")
    image.paste(overlay_image, (0, 0), overlay_image)

    return image_to_bytes(image)
