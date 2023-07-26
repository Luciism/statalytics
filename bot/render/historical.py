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
        stats = HistoricalStats(name, uuid, identifier, mode, hypixel_data)
    else:
        stats = LookbackStats(name, uuid, period, mode, hypixel_data)

    level = stats.level
    rank_info = stats.rank_info

    progress, target, progress_of_10 = stats.progress
    timezone, reset_hour = stats.get_time_info()
    most_played = stats.get_most_played()
    games_played = f'{stats.games_played:,}'
    items_purchased = f'{stats.items_purchased:,}'
    stars_gained = stats.stars_gained

    wins, losses, wlr = stats.get_wins()
    final_kills, final_deaths, fkdr = stats.get_finals()
    beds_broken, beds_lost, bblr = stats.get_beds()
    kills, deaths, kdr = stats.get_kills()

    image = get_background(
        path=f'./assets/bg/historical/{identifier}', uuid=uuid,
        default='base', level=level, rank_info=rank_info
    ).convert("RGBA")

    minecraft_16 = ImageFont.truetype('./assets/fonts/minecraft.ttf', 16)
    minecraft_17 = ImageFont.truetype('./assets/fonts/minecraft.ttf', 17)

    # Render the stat values
    data = [
        {'position': (87, 190), 'text': f'&a{wins}'},
        {'position': (241, 190), 'text': f'&c{losses}'},
        {'position': (378, 190), 'text': f'&6{wlr}'},
        {'position': (87, 249), 'text': f'&a{final_kills}'},
        {'position': (241, 249), 'text': f'&c{final_deaths}'},
        {'position': (378, 249), 'text': f'&6{fkdr}'},
        {'position': (87, 308), 'text': f'&a{beds_broken}'},
        {'position': (241, 308), 'text': f'&c{beds_lost}'},
        {'position': (378, 308), 'text': f'&6{bblr}'},
        {'position': (87, 367), 'text': f'&a{kills}'},
        {'position': (241, 367), 'text': f'&c{deaths}'},
        {'position': (378, 367), 'text': f'&6{kdr}'},
        {'position': (82, 427), 'text': f'&d{stars_gained}'},
        {'position': (226, 427), 'text': f'&d{timezone}'},
        {'position': (370, 427), 'text': f'&d{reset_hour}'},
        {'position': (537, 249), 'text': f'&d{games_played}'},
        {'position': (537, 308), 'text': f'&d{most_played}'},
        {'position': (537, 367), 'text': f'&d{relative_date}'},
        {'position': (537, 427), 'text': f'&d{items_purchased}'},
        {'position': (537, 46), 'text': f'({mode.title()})'}
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
