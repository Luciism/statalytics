from calc.compare import CompareStats
import statalib as lib
from statalib import HypixelData, Mode, to_thread, REL_PATH

from statalib.render import ImageRender, BackgroundImageLoader


bg = BackgroundImageLoader(dir="compare")

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
    mode: Mode,
    hypixel_data_1: HypixelData,
    hypixel_data_2: HypixelData,
    save_dir: str
) -> None:
    stats = CompareStats(hypixel_data_1, hypixel_data_2, mode)
    im = ImageRender(bg.load_background_image(
        uuid_1, {"level": stats.level_1, "rank_info": stats.rank_info_1}))

    # Render the stat values
    im.text.draw_many([
        (f'&a{stats.wins_comp}', {'position': (114, 110)}),
        (color(stats.wins_diff, "g"), {'position': (114, 144)}),
        (f'&c{stats.losses_comp}', {'position': (320, 110)}),
        (color(stats.losses_diff, "b"), {'position': (320, 144)}),
        (f'&6{stats.wlr_comp}', {'position': (526, 110)}),
        (color(stats.wlr_diff, "g"), {'position': (526, 144)}),
        (f'&a{stats.final_kills_comp}', {'position': (114, 208)}),
        (color(stats.final_kills_diff, "g"), {'position': (114, 242)}),
        (f'&c{stats.final_deaths_comp}', {'position': (320, 208)}),
        (color(stats.final_deaths_diff, "b"), {'position': (320, 242)}),
        (f'&6{stats.fkdr_comp}', {'position': (526, 208)}),
        (color(stats.fkdr_diff, "g"), {'position': (526, 242)}),
        (f'&a{stats.beds_broken_comp}', {'position': (114, 306)}),
        (color(stats.beds_broken_diff, "g"), {'position': (114, 340)}),
        (f'&c{stats.beds_lost_comp}', {'position': (320, 306)}),
        (color(stats.beds_lost_diff, "b"), {'position': (320, 340)}),
        (f'&6{stats.bblr_comp}', {'position': (526, 306)}),
        (color(stats.bblr_diff, "g"), {'position': (526, 340)}),
        (f'&a{stats.kills_comp}', {'position': (114, 404)}),
        (color(stats.kills_diff, "g"), {'position': (114, 438)}),
        (f'&c{stats.deaths_comp}', {'position': (320, 404)}),
        (color(stats.deaths_diff, "b"), {'position': (320, 438)}),
        (f'&6{stats.kdr_comp}', {'position': (526, 404)}),
        (color(stats.kdr_diff, "g"), {'position': (526, 438)}),
        (f'({stats._bw_1.title_mode})', {'position': (526, 47)}),
    ], default_text_options={
        "shadow_offset": (2, 2), "align": "center", "font_size": 16}
    )


    im.player.render_hypixel_username(
        name_1, stats.rank_info_1, text_options={
        "align": "center",
        "font_size": 18,
        "position": (225, 14)
    })

    im.player.render_hypixel_username(
        name_2, stats.rank_info_2, text_options={
        "align": "center",
        "font_size": 18,
        "position": (225, 51)
    })

    # Paste overlay image
    im.overlay_image(lib.ASSET_LOADER.load_image("bg/compare/overlay.png"))

    # Save the image
    im.save(f'{REL_PATH}/database/rendered/{save_dir}/{mode.id}.png')
