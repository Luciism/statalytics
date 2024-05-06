from calc.average import AverageStats
import statalib as lib
from statalib import to_thread, REL_PATH
from statalib.render import (
    render_display_name,
    get_background,
    paste_skin,
    render_progress_bar,
    render_progress_text,
    render_mc_text
)


@to_thread
def render_average(
    name: str,
    uuid: str,
    mode: str,
    hypixel_data: dict,
    skin_model: bytes,
    save_dir: str
):
    stats = AverageStats(hypixel_data, mode)
    progress, target, xp_bar_progress = stats.progress

    image = get_background(
        bg_dir='average', uuid=uuid, level=stats.level, rank_info=stats.rank_info
    ).convert("RGBA")

    # Render the stat values
    data = [
        {'position': (88, 249), 'text': f'&a{stats.wins_per_star}'},
        {'position': (88, 309), 'text': f'&a{stats.final_kills_per_star}'},
        {'position': (88, 369), 'text': f'&a{stats.beds_broken_per_star}'},
        {'position': (88, 429), 'text': f'&a{stats.kills_per_star}'},

        {'position': (242, 249), 'text': f'&c{stats.losses_per_star}'},
        {'position': (242, 309), 'text': f'&c{stats.final_deaths_per_star}'},
        {'position': (242, 369), 'text': f'&c{stats.beds_lost_per_star}'},
        {'position': (242, 429), 'text': f'&c{stats.deaths_per_star}'},

        {'position': (396, 249), 'text': f'&a{stats.most_wins_mode}'},
        {'position': (396, 309), 'text': f'&a{stats.final_kills_per_game}'},
        {'position': (396, 369), 'text': f'&a{stats.beds_broken_per_game}'},
        {'position': (396, 429), 'text': f'&a{stats.kills_per_game}'},

        {'position': (551, 249), 'text': f'&c{stats.most_losses_mode}'},
        {'position': (551, 309), 'text': f'&c{stats.games_per_final_death}'},
        {'position': (551, 369), 'text': f'&c{stats.games_per_bed_lost}'},
        {'position': (551, 429), 'text': f'&c{stats.deaths_per_game}'},

        {'position': (83, 189), 'text': f'&a{stats.clutch_rate}'},
        {'position': (225, 189), 'text': f'&a{stats.win_rate}'},
        {'position': (368, 189), 'text': f'&c{stats.loss_rate}'},

        {'position': (536, 46), 'text': f'&f({stats.title_mode})'}
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
        username=name,
        rank_info=stats.rank_info,
        image=image,
        font_size=22,
        position=(225, 26),
        align='center'
    )

    render_progress_bar(
        level=stats.level,
        xp_bar_progress=xp_bar_progress,
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
        text='Avg Stats',
        position=(536, 25),
        font_size=18,
        image=image,
        shadow_offset=(2, 2),
        align='center'
    )

    # Paste overlay image
    overlay_image = lib.ASSET_LOADER.load_image("bg/average/overlay.png")\
        .convert("RGBA")
    image.paste(overlay_image, (0, 0), overlay_image)

    # Render skin
    paste_skin(skin_model, image, positions=(465, 67))

    # Save the image
    image.save(f'{REL_PATH}/database/rendered/{save_dir}/{mode.lower()}.png')
