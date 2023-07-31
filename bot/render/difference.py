from PIL import Image, ImageFont

from calc.difference import Difference
from statalib import to_thread
from statalib.render import (
    render_display_name,
    get_background,
    paste_skin,
    render_progress_bar,
    render_progress_text,
    render_mc_text
)


@to_thread
def render_difference(
    name: str,
    uuid: str, 
    relative_date: str,
    method: str,
    mode: str,
    hypixel_data: dict,
    skin_res: bytes,
    save_dir: str
):
    diffs = Difference(uuid, method, hypixel_data, mode)

    level = diffs.level
    rank_info = diffs.rank_info
    progress, target, progress_of_10 = diffs.progress
    stars_gained = diffs.get_stars_gained()

    wins, losses, wlr_1, wlr_2, wlr_diff = diffs.get_wins()
    final_kills, final_deaths, fkdr_1, fkdr_2, fkdr_diff = diffs.get_finals()
    beds_broken, beds_lost, bblr_1, bblr_2, bblr_diff = diffs.get_beds()
    kills, deaths, kdr_1, kdr_2, kdr_diff = diffs.get_kills()

    image = get_background(
        path='./assets/bg/difference', uuid=uuid,
        default='base', level=level, rank_info=rank_info
    ).convert("RGBA")

    minecraft_16 = ImageFont.truetype('./assets/fonts/minecraft.ttf', 16)
    minecraft_18 = ImageFont.truetype('./assets/fonts/minecraft.ttf', 18)

    def diff_color(diff: str) -> tuple:
        if diff[1] == '+':
            return '&a'
        return '&c'

    # Render the stat values
    data = [
        {'position': (88, 249), 'text': f'&a{wins}'},
        {'position': (88, 309), 'text': f'&a{final_kills}'},
        {'position': (88, 369), 'text': f'&a{beds_broken}'},
        {'position': (88, 429), 'text': f'&a{kills}'},
        {'position': (242, 249), 'text': f'&c{losses}'},
        {'position': (242, 309), 'text': f'&c{final_deaths}'},
        {'position': (242, 369), 'text': f'&c{beds_lost}'},
        {'position': (242, 429), 'text': f'&c{deaths}'},

        {'position': (474, 249),
         'text': f'&6{wlr_1} &f-> &6{wlr_2} {diff_color(wlr_diff)}{wlr_diff}'},

        {'position': (474, 309),
         'text': f'&6{fkdr_1} &f-> &6{fkdr_2} {diff_color(fkdr_diff)}{fkdr_diff}'},

        {'position': (474, 369),
         'text': f'&6{bblr_1} &f-> &6{bblr_2} {diff_color(bblr_diff)}{bblr_diff}'},

        {'position': (474, 429),
         'text': f'&6{kdr_1} &f-> &6{kdr_2} {diff_color(kdr_diff)}{kdr_diff}'},

        {'position': (118, 189), 'text': f'&d{stars_gained}'},
        {'position': (332, 189), 'text': f'&d{relative_date}'},
        {'position': (536, 46), 'text': f'({mode.title()})'}
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
        rank_info=rank_info,
        image=image,
        font_size=22,
        position=(225, 26),
        align='center'
    )

    render_progress_bar(
        level=level,
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
        font=minecraft_18,
        image=image,
        shadow_offset=(2, 2),
        align='center'
    )

    # Paste overlay image
    overlay_image = Image.open('./assets/bg/difference/overlay.png')
    overlay_image = overlay_image.convert("RGBA")
    image.paste(overlay_image, (0, 0), overlay_image)

    # Render skin
    paste_skin(skin_res, image, positions=(465, 67))

    # Save the image
    image.save(f'./database/rendered/{save_dir}/{mode.lower()}.png')
