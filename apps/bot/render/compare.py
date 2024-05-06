from calc.compare import CompareStats
import statalib as lib
from statalib import to_thread, REL_PATH
from statalib.render import (
    render_display_name,
    get_background,
    render_mc_text
)


def color(value, method):
    """method `g` for good `b` for bad"""
    if method == 'g':
        color = '&a' if value[0] == '+' else '&c'
    else:
        color = '&c' if value[0] == '+' else '&a'
    return f'{color}{value}'


@to_thread
def render_compare(
    name_1: str,
    name_2: str,
    uuid_1: str,
    mode: str,
    hypixel_data_1: dict,
    hypixel_data_2: dict,
    save_dir: str
):
    stats = CompareStats(hypixel_data_1, hypixel_data_2, mode)
    stats.__setattr__('yourmom', 'test')
    stats.yourmom
    image = get_background(
        bg_dir='compare', uuid=uuid_1, level=stats.level_1, rank_info=stats.rank_info_1
    ).convert("RGBA")

    # Render the stat values
    data = [
        {'position': (114, 110), 'text': f'&a{stats.wins_comp}'},
        {'position': (114, 144), 'text': color(stats.wins_diff, "g")},
        {'position': (320, 110), 'text': f'&c{stats.losses_comp}'},
        {'position': (320, 144), 'text': color(stats.losses_diff, "b")},
        {'position': (526, 110), 'text': f'&6{stats.wlr_comp}'},
        {'position': (526, 144), 'text': color(stats.wlr_diff, "g")},
        {'position': (114, 208), 'text': f'&a{stats.final_kills_comp}'},
        {'position': (114, 242), 'text': color(stats.final_kills_diff, "g")},
        {'position': (320, 208), 'text': f'&c{stats.final_deaths_comp}'},
        {'position': (320, 242), 'text': color(stats.final_deaths_diff, "b")},
        {'position': (526, 208), 'text': f'&6{stats.fkdr_comp}'},
        {'position': (526, 242), 'text': color(stats.fkdr_diff, "g")},
        {'position': (114, 306), 'text': f'&a{stats.beds_broken_comp}'},
        {'position': (114, 340), 'text': color(stats.beds_broken_diff, "g")},
        {'position': (320, 306), 'text': f'&c{stats.beds_lost_comp}'},
        {'position': (320, 340), 'text': color(stats.beds_lost_diff, "b")},
        {'position': (526, 306), 'text': f'&6{stats.bblr_comp}'},
        {'position': (526, 340), 'text': color(stats.bblr_diff, "g")},
        {'position': (114, 404), 'text': f'&a{stats.kills_comp}'},
        {'position': (114, 438), 'text': color(stats.kills_diff, "g")},
        {'position': (320, 404), 'text': f'&c{stats.deaths_comp}'},
        {'position': (320, 438), 'text': color(stats.deaths_diff, "b")},
        {'position': (526, 404), 'text': f'&6{stats.kdr_comp}'},
        {'position': (526, 438), 'text': color(stats.kdr_diff, "g")},
        {'position': (526, 47), 'text': f'({stats._bw_1.title_mode})'}
    ]

    for values in data:
        render_mc_text(
            image=image,
            shadow_offset=(2, 2),
            align='center',
            font=lib.ASSET_LOADER.load_font("main.ttf", 16),
            **values
        )

    render_display_name(
        username=name_1,
        rank_info=stats.rank_info_1,
        level=stats.level_1,
        image=image,
        font_size=18,
        position=(225, 14),
        align='center'
    )

    render_display_name(
        username=name_2,
        rank_info=stats.rank_info_2,
        level=stats.level_2,
        image=image,
        font_size=18,
        position=(225, 51),
        align='center'
    )

    # Paste overlay image
    overlay_image = lib.ASSET_LOADER.load_image("bg/compare/overlay.png")
    overlay_image = overlay_image.convert("RGBA")
    image.paste(overlay_image, (0, 0), overlay_image)

    # Save the image
    image.save(f'{REL_PATH}/database/rendered/{save_dir}/{mode.lower()}.png')
