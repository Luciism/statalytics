from calc.total import TotalStats
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
def render_total(
    name: str,
    uuid: str,
    mode: str,
    hypixel_data: dict,
    skin_model: bytes,
    save_dir: str
):
    stats = TotalStats(hypixel_data, mode)
    progress, target, xp_bar_progress = stats.progress

    image = get_background(
        bg_dir='total', uuid=uuid, level=stats.level, rank_info=stats.rank_info
    ).convert("RGBA")

    # Render the stat values
    data = [
        {'position': (87, 190), 'text': f'&a{stats.wins:,}'},
        {'position': (241, 190), 'text': f'&c{stats.losses:,}'},
        {'position': (378, 190), 'text': f'&6{stats.wlr:,}'},
        {'position': (87, 249), 'text': f'&a{stats.final_kills:,}'},
        {'position': (241, 249), 'text': f'&c{stats.final_deaths:,}'},
        {'position': (378, 249), 'text': f'&6{stats.fkdr:,}'},
        {'position': (87, 308), 'text': f'&a{stats.beds_broken:,}'},
        {'position': (241, 308), 'text': f'&c{stats.beds_lost:,}'},
        {'position': (378, 308), 'text': f'&6{stats.bblr:,}'},
        {'position': (87, 367), 'text': f'&a{stats.kills:,}'},
        {'position': (241, 367), 'text': f'&c{stats.deaths:,}'},
        {'position': (378, 367), 'text': f'&6{stats.kdr:,}'},
        {'position': (82, 427), 'text': f'&d{stats.winstreak_str}'},
        {'position': (226, 427), 'text': f'&d{stats.loot_chests:,}'},
        {'position': (370, 427), 'text': f'&d{stats.coins:,}'},
        {'position': (537, 250), 'text': f'&d{stats.games_played:,}'},
        {'position': (537, 309), 'text': f'&d{stats.most_played}'},
        {'position': (537, 368), 'text': f'&d{stats.void_deaths:,}'},
        {'position': (537, 427), 'text': f'&d{stats.items_purchased:,}'},
        {'position': (537, 46), 'text': f'({stats.title_mode})'}
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

    # Paste overlay image
    overlay_image = lib.ASSET_LOADER.load_image("bg/total/overlay_generic.png")
    overlay_image = overlay_image.convert("RGBA")
    image.paste(overlay_image, (0, 0), overlay_image)

    # Save the image
    image.save(f'{REL_PATH}/database/rendered/{save_dir}/{mode.lower()}.png')
