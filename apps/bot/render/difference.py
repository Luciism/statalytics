from PIL import Image, ImageFont

from calc.difference import DifferenceStats
from statalib import to_thread, REL_PATH
from statalib.render import (
    render_display_name,
    get_background,
    paste_skin,
    render_progress_bar,
    render_progress_text,
    render_mc_text
)


def color(diff: str) -> tuple:
    if diff[1] == '+':
        return f'&a{diff}'
    return f'&c{diff}'


@to_thread
def render_difference(
    name: str,
    uuid: str,
    relative_date: str,
    method: str,
    mode: str,
    hypixel_data: dict,
    skin_model: bytes,
    save_dir: str
):
    stats = DifferenceStats(uuid, method, hypixel_data, mode)
    progress, target, progress_of_10 = stats.progress

    image = get_background(
        bg_dir='difference', uuid=uuid, level=stats.level, rank_info=stats.rank_info
    ).convert("RGBA")

    minecraft_16 = ImageFont.truetype(f'{REL_PATH}/assets/fonts/minecraft.ttf', 16)

    # Render the stat values
    data = [
        {'position': (88, 249), 'text': f'&a{stats.wins_cum}'},
        {'position': (88, 309), 'text': f'&a{stats.final_kills_cum}'},
        {'position': (88, 369), 'text': f'&a{stats.beds_broken_cum}'},
        {'position': (88, 429), 'text': f'&a{stats.kills_cum}'},
        {'position': (242, 249), 'text': f'&c{stats.losses_cum}'},
        {'position': (242, 309), 'text': f'&c{stats.final_deaths_cum}'},
        {'position': (242, 369), 'text': f'&c{stats.beds_lost_cum}'},
        {'position': (242, 429), 'text': f'&c{stats.deaths_cum}'},

        {'position': (474, 249), 'text':
         f'&6{stats.wlr_old} &f➡ &6{stats.wlr_new} {color(stats.wlr_diff)}'},

        {'position': (474, 309), 'text':
         f'&6{stats.fkdr_old} &f➡ &6{stats.fkdr_new} {color(stats.fkdr_diff)}'},

        {'position': (474, 369), 'text':
         f'&6{stats.bblr_old} &f➡ &6{stats.bblr_new} {color(stats.bblr_diff)}'},

        {'position': (474, 429), 'text':
         f'&6{stats.kdr_old} &f➡ &6{stats.kdr_new} {color(stats.kdr_diff)}'},

        {'position': (118, 189), 'text': f'&d{stats.stars_gained}'},
        {'position': (332, 189), 'text': f'&d{relative_date}'},
        {'position': (536, 46), 'text': f'({stats.title_mode})'}
    ]

    for values in data:
        render_mc_text(
            image=image,
            shadow_offset=(2, 2),
            align='center',
            font=minecraft_16,
            **values
        )

    render_display_name(
        username=name,
        rank_info=stats.rank_info,
        image=image,
        font_size=22,
        position=(225, 26),
        align='center'
    )

    render_progress_bar(
        level=stats.level,
        progress_of_10=progress_of_10,
        position=(225, 88),
        image=image,
        align='center'
    )

    render_progress_text(
        progress=progress,
        target=target,
        position=(225, 119),
        image=image,
        align='center'
    )

    render_mc_text(
        text=f'{method.title()} Diffs',
        position=(536, 25),
        font_size=18,
        image=image,
        shadow_offset=(2, 2),
        align='center'
    )

    # Paste overlay image
    overlay_image = Image.open(f'{REL_PATH}/assets/bg/difference/overlay.png')
    overlay_image = overlay_image.convert("RGBA")
    image.paste(overlay_image, (0, 0), overlay_image)

    # Render skin
    paste_skin(skin_model, image, positions=(465, 67))

    # Save the image
    image.save(f'{REL_PATH}/database/rendered/{save_dir}/{mode.lower()}.png')
