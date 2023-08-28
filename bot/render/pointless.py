from PIL import Image, ImageFont

from calc.total import TotalStats
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
def render_pointless(
    name: str,
    uuid: str,
    mode: str,
    hypixel_data: dict,
    skin_model: bytes,
    save_dir: str,
):
    stats = TotalStats(hypixel_data, mode)
    progress, target, progress_of_10 = stats.progress

    image = get_background(
        bg_dir='total', uuid=uuid, level=stats.level, rank_info=stats.rank_info
    ).convert("RGBA")

    minecraft_16 = ImageFont.truetype('./assets/fonts/minecraft.ttf', 16)

    # Render the stat values
    data = [
        {'position': (87, 190), 'text': f'&a{stats.falling_kills:,}'},
        {'position': (241, 190), 'text': f'&c{stats.falling_deaths:,}'},
        {'position': (378, 190), 'text': f'&6{stats.falling_kdr:,}'},
        {'position': (87, 249), 'text': f'&a{stats.void_kills:,}'},
        {'position': (241, 249), 'text': f'&c{stats.void_deaths:,}'},
        {'position': (378, 249), 'text': f'&6{stats.void_kdr:,}'},
        {'position': (87, 308), 'text': f'&a{stats.projectile_kills:,}'},
        {'position': (241, 308), 'text': f'&c{stats.projectile_deaths:,}'},
        {'position': (378, 308), 'text': f'&6{stats.projectile_kdr:,}'},
        {'position': (87, 367), 'text': f'&a{stats.fire_kills:,}'},
        {'position': (241, 367), 'text': f'&c{stats.fire_deaths:,}'},
        {'position': (378, 367), 'text': f'&6{stats.fire_kdr:,}'},
        {'position': (82, 427), 'text': f'&d{stats.winstreak_str}'},
        {'position': (226, 427), 'text': f'&d{stats.loot_chests:,}'},
        {'position': (370, 427), 'text': f'&d{stats.coins:,}'},
        {'position': (537, 250), 'text': f'&d{stats.games_played:,}'},
        {'position': (537, 309), 'text': f'&d{stats.most_played}'},
        {'position': (537, 368), 'text': f'&d{stats.tools_purchased:,}'},
        {'position': (537, 427), 'text': f'&d{stats.melee_kills:,}'},
        {'position': (537, 46), 'text': f'({stats.title_mode})'}
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
        rank_info=stats.rank_info,
        image=image,
        font_size=22,
        position=(226, 31),
        align='center'
    )

    render_progress_bar(
        level=stats.level,
        progress_of_10=progress_of_10,
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

    # Paste overlay image
    overlay_image = Image.open(f'./assets/bg/total/overlay_pointless.png')
    overlay_image = overlay_image.convert("RGBA")
    image.paste(overlay_image, (0, 0), overlay_image)

    # Save the image
    image.save(f'./database/rendered/{save_dir}/{mode.lower()}.png')
