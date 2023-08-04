from PIL import Image, ImageFont

from calc.historical import HistoricalStats, LookbackStats
from statalib import TRACKERS, to_thread
from statalib.render import (
    render_display_name,
    get_background,
    paste_skin,
    render_progress_bar,
    render_progress_text,
    render_mc_text
)


@to_thread
def render_historical(
    name: str,
    uuid: str,
    identifier: str,
    relative_date: str,
    title: str,
    mode: str,
    hypixel_data: dict,
    skin_res: bytes,
    save_dir: str,
    period: str=None
):
    if identifier in TRACKERS:
        stats = HistoricalStats(uuid, identifier, hypixel_data, mode)
    else:
        stats = LookbackStats(uuid, period, hypixel_data, mode)

    level = stats.level
    rank_info = stats.rank_info

    progress, target, progress_of_10 = stats.progress

    image = get_background(
        path=f'./assets/bg/historical/{identifier}', uuid=uuid,
        default='base', level=level, rank_info=rank_info
    ).convert("RGBA")

    minecraft_16 = ImageFont.truetype('./assets/fonts/minecraft.ttf', 16)
    minecraft_17 = ImageFont.truetype('./assets/fonts/minecraft.ttf', 17)

    # Render the stat values
    data = [
        {'position': (87, 190), 'text': f'&a{stats.wins_cum:,}'},
        {'position': (241, 190), 'text': f'&c{stats.losses_cum:,}'},
        {'position': (378, 190), 'text': f'&6{stats.wlr_cum:,}'},
        {'position': (87, 249), 'text': f'&a{stats.final_kills_cum:,}'},
        {'position': (241, 249), 'text': f'&c{stats.final_deaths_cum:,}'},
        {'position': (378, 249), 'text': f'&6{stats.fkdr_cum:,}'},
        {'position': (87, 308), 'text': f'&a{stats.beds_broken_cum:,}'},
        {'position': (241, 308), 'text': f'&c{stats.beds_lost_cum:,}'},
        {'position': (378, 308), 'text': f'&6{stats.bblr_cum:,}'},
        {'position': (87, 367), 'text': f'&a{stats.kills_cum:,}'},
        {'position': (241, 367), 'text': f'&c{stats.deaths_cum:,}'},
        {'position': (378, 367), 'text': f'&6{stats.kdr_cum:,}'},
        {'position': (82, 427), 'text': f'&d{stats.stars_gained}'},
        {'position': (226, 427), 'text': f'&d{stats.timezone}'},
        {'position': (370, 427), 'text': f'&d{stats.reset_hour}'},
        {'position': (537, 249), 'text': f'&d{stats.games_played_cum:,}'},
        {'position': (537, 308), 'text': f'&d{stats.most_played_cum}'},
        {'position': (537, 367), 'text': f'&d{relative_date}'},
        {'position': (537, 427), 'text': f'&d{stats.items_purchased_cum:,}'},
        {'position': (537, 46), 'text': f'({stats.title_mode})'}
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
        position=(226, 31),
        align='center'
    )

    render_progress_bar(
        level=level,
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

    render_mc_text(
        text=title,
        position=(537, 27),
        font=minecraft_17,
        image=image,
        shadow_offset=(2, 2),
        align='center'
    )

    # Paste skin
    paste_skin(skin_res, image, positions=(466, 69))

    # Paste overlay
    overlay_image = Image.open('./assets/bg/historical/overlay.png')
    overlay_image = overlay_image.convert("RGBA")
    image.paste(overlay_image, (0, 0), overlay_image)

    # Save the image
    image.save(f'./database/rendered/{save_dir}/{mode.lower()}.png')
