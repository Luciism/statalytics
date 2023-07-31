from PIL import Image, ImageFont

from calc.session import SessionStats
from statalib import to_thread
from statalib.render import (
    render_display_name,
    get_background,
    paste_skin,
    render_progress_bar,
    render_mc_text
)


@to_thread
def render_session(
    name: str,
    uuid: str,
    session: int,
    mode: str,
    hypixel_data: dict,
    skin_res: bytes,
    save_dir: str
):
    stats = SessionStats(uuid, session, hypixel_data, mode)

    progress_of_10 = stats.progress[2]
    total_sessions = stats.total_sessions

    rank_info = stats.rank_info
    most_played = stats.get_most_played()
    level = stats.level
    date_started = stats.date_started

    wins, losses, wlr = stats.get_wins()
    final_kills, final_deaths, fkdr = stats.get_finals()
    beds_broken, beds_lost, bblr = stats.get_beds()
    kills, deaths, kdr = stats.get_kills()

    wins_per_day, finals_per_day, beds_per_day,\
        stars_per_day = stats.get_per_day()

    image = get_background(
        path='./assets/bg/session', uuid=uuid,
        default='base', level=level, rank_info=rank_info
    ).convert("RGBA")

    minecraft_16 = ImageFont.truetype('./assets/fonts/minecraft.ttf', 16)

    # Render the stat values
    data = [
        {'position': (87, 131), 'text': f'&a{wins}'},
        {'position': (241, 131), 'text': f'&c{losses}'},
        {'position': (378, 131), 'text': f'&6{wlr}'},
        {'position': (87, 190), 'text': f'&a{final_kills}'},
        {'position': (241, 190), 'text': f'&c{final_deaths}'},
        {'position': (378, 190), 'text': f'&6{fkdr}'},
        {'position': (87, 249), 'text': f'&a{beds_broken}'},
        {'position': (241, 249), 'text': f'&c{beds_lost}'},
        {'position': (378, 249), 'text': f'&6{bblr}'},
        {'position': (87, 308), 'text': f'&a{kills}'},
        {'position': (241, 308), 'text': f'&c{deaths}'},
        {'position': (378, 308), 'text': f'&6{kdr}'},
        {'position': (82, 368), 'text': f'&d{stars_per_day}'},
        {'position': (226, 368), 'text': f'&d{stats.stars_gained}'},
        {'position': (370, 368), 'text': f'&d{stats.games_played}'},
        {'position': (82, 427), 'text': f'&d{wins_per_day}'},
        {'position': (226, 427), 'text': f'&d{finals_per_day}'},
        {'position': (370, 427), 'text': f'&d{beds_per_day}'},
        {'position': (537, 250), 'text': f'&d# {session}'},
        {'position': (537, 309), 'text': f'&d{total_sessions}'},
        {'position': (537, 368), 'text': f'&d{date_started}'},
        {'position': (537, 427), 'text': f'&d{most_played}'},
        {'position': (537, 46), 'text': f'({mode.title()})'}
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
        position=(226, 30),
        align='center'
    )

    render_progress_bar(
        level=level,
        progress_of_10=progress_of_10,
        position=(226, 61),
        image=image,
        align='center'
    )

    paste_skin(skin_res, image, positions=(466, 69))

    # Paste overlay image
    overlay_image = Image.open('./assets/bg/session/overlay.png')
    overlay_image = overlay_image.convert("RGBA")
    image.paste(overlay_image, (0, 0), overlay_image)

    # Save the image
    image.save(f'./database/rendered/{save_dir}/{mode.lower()}.png')
