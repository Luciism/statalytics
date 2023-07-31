from PIL import Image, ImageFont

from calc.compare import CompareStats
from statalib import to_thread
from statalib.render import (
    render_display_name,
    get_background,
    render_mc_text
)


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

    level_1, level_2 = stats.level_1, stats.level_2
    rank_info_1, rank_info_2 = stats.rank_info_1, stats.rank_info_2

    wins, losses, wlr, wins_diff, losses_diff, wlr_diff = stats.get_wins()
    fks, fds, fkdr, fks_diff, fds_diff, fkdr_diff = stats.get_finals()
    bsb, bsl, bblr, bsb_diff, bsl_diff, bblr_diff = stats.get_beds()
    kills, deaths, kdr, kills_diff, deaths_diff, kdr_diff = stats.get_kills()

    image = get_background(
        path='./assets/bg/compare', uuid=uuid_1,
        default='base', level=level_1, rank_info=rank_info_1
    ).convert("RGBA")

    minecraft_16 = ImageFont.truetype('./assets/fonts/minecraft.ttf', 16)

    def color(value, method):
        if method == 'g':
            return '&a' if value[0] == '+' else '&c'
        return '&c' if value[0] == '+' else '&a'

    # Render the stat values
    data = [
        {'position': (114, 110), 'text': f'&a{wins}'},
        {'position': (114, 144), 'text': f'{color(wins_diff, "g")}{wins_diff}'},
        {'position': (320, 110), 'text': f'&c{losses}'},
        {'position': (320, 144), 'text': f'{color(losses_diff, "b")}{losses_diff}'},
        {'position': (526, 110), 'text': f'&6{wlr}'},
        {'position': (526, 144), 'text': f'{color(wlr_diff, "g")}{wlr_diff}'},
        {'position': (114, 208), 'text': f'&a{fks}'},
        {'position': (114, 242), 'text': f'{color(fks_diff, "g")}{fks_diff}'},
        {'position': (320, 208), 'text': f'&c{fds}'},
        {'position': (320, 242), 'text': f'{color(fds_diff, "b")}{fds_diff}'},
        {'position': (526, 208), 'text': f'&6{fkdr}'},
        {'position': (526, 242), 'text': f'{color(fkdr_diff, "g")}{fkdr_diff}'},
        {'position': (114, 306), 'text': f'&a{bsb}'},
        {'position': (114, 340), 'text': f'{color(bsb_diff, "g")}{bsb_diff}'},
        {'position': (320, 306), 'text': f'&c{bsl}'},
        {'position': (320, 340), 'text': f'{color(bsl_diff, "b")}{bsl_diff}'},
        {'position': (526, 306), 'text': f'&6{bblr}'},
        {'position': (526, 340), 'text': f'{color(bblr_diff, "g")}{bblr_diff}'},
        {'position': (114, 404), 'text': f'&a{kills}'},
        {'position': (114, 438), 'text': f'{color(kills_diff, "g")}{kills_diff}'},
        {'position': (320, 404), 'text': f'&c{deaths}'},
        {'position': (320, 438), 'text': f'{color(deaths_diff, "b")}{deaths_diff}'},
        {'position': (526, 404), 'text': f'&6{kdr}'},
        {'position': (526, 438), 'text': f'{color(kdr_diff, "g")}{kdr_diff}'},
        {'position': (526, 47), 'text': f'({mode})'}
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
        username=name_1,
        rank_info=rank_info_1,
        level=level_1,
        image=image,
        font_size=18,
        position=(225, 14),
        align='center'
    )

    render_display_name(
        username=name_2,
        rank_info=rank_info_2,
        level=level_2,
        image=image,
        font_size=18,
        position=(225, 51),
        align='center'
    )

    # Paste overlay image
    overlay_image = Image.open('./assets/bg/compare/overlay.png')
    overlay_image = overlay_image.convert("RGBA")
    image.paste(overlay_image, (0, 0), overlay_image)

    # Save the image
    image.save(f'./database/rendered/{save_dir}/{mode.lower()}.png')
