from PIL import Image, ImageFont

from calc.resources import ResourcesStats
from statalib import to_thread
from statalib.render import (
    render_display_name,
    get_background,
    render_progress_text,
    render_progress_bar,
    render_mc_text
)


@to_thread
def render_resources(
    name: str,
    uuid: str,
    mode: str,
    hypixel_data: dict,
    save_dir: str
):
    stats = ResourcesStats(hypixel_data, mode)

    level = stats.level
    progress, target, progress_of_10 = stats.progress

    rank_info = stats.rank_info

    total_collected = f'{stats.stats_collected:,}'
    iron_collected = f'{stats.iron_collected:,}'
    gold_collected = f'{stats.gold_collected:,}'
    dias_collected = f'{stats.diamonds_collected:,}'
    ems_collected = f'{stats.emeralds_collected:,}'

    iron_per_game, gold_per_game, dias_per_game,\
        ems_per_game = stats.get_per_game()

    iron_per_star, gold_per_star, dias_per_star,\
        ems_per_star = stats.get_per_star()

    iron_percent, gold_percent, dia_percent,\
        em_percent = stats.get_percentages()

    iron_most_mode, gold_most_mode, dia_most_mode,\
        em_most_mode = stats.get_most_modes()

    image = get_background(
        path='./assets/bg/resources', uuid=uuid,
        default='base', level=level, rank_info=rank_info
    ).convert("RGBA")

    minecraft_16 = ImageFont.truetype('./assets/fonts/minecraft.ttf', 16)

    # Render the stat values
    data = [
        {'position': (89, 189), 'text': f'&f{iron_collected}'},
        {'position': (244, 189), 'text': f'&6{gold_collected}'},
        {'position': (399, 189), 'text': f'&b{dias_collected}'},
        {'position': (553, 189), 'text': f'&a{ems_collected}'},

        {'position': (89, 249), 'text': f'&f{iron_per_game}'},
        {'position': (244, 249), 'text': f'&6{gold_per_game}'},
        {'position': (399, 249), 'text': f'&b{dias_per_game}'},
        {'position': (553, 249), 'text': f'&a{ems_per_game}'},

        {'position': (89, 309), 'text': f'&f{iron_per_star}'},
        {'position': (244, 309), 'text': f'&6{gold_per_star}'},
        {'position': (399, 309), 'text': f'&b{dias_per_star}'},
        {'position': (553, 309), 'text': f'&a{ems_per_star}'},

        {'position': (89, 369), 'text': f'&f{iron_percent}'},
        {'position': (244, 369), 'text': f'&6{gold_percent}'},
        {'position': (399, 369), 'text': f'&b{dia_percent}'},
        {'position': (553, 369), 'text': f'&a{em_percent}'},

        {'position': (89, 429), 'text': f'&f{iron_most_mode}'},
        {'position': (244, 429), 'text': f'&6{gold_most_mode}'},
        {'position': (399, 429), 'text': f'&b{dia_most_mode}'},
        {'position': (553, 429), 'text': f'&a{em_most_mode}'},

        {'position': (537, 129), 'text': f'&d{total_collected}'},
        {'position': (537, 65), 'text': f'({mode})'}
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
        position=(226, 27),
        align='center'
    )

    render_progress_bar(
        level=level,
        progress_of_10=progress_of_10,
        position=(226, 88),
        image=image,
        align='center'
    )

    render_progress_text(
        progress=progress,
        target=target,
        position=(226, 119),
        image=image,
        align='center'
    )

    # Paste overlay image
    overlay_image = Image.open('./assets/bg/resources/overlay.png')
    overlay_image = overlay_image.convert("RGBA")
    image.paste(overlay_image, (0, 0), overlay_image)

    # Save the image
    image.save(f'./database/rendered/{save_dir}/{mode.lower()}.png')
