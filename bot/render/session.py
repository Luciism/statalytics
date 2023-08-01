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

    image = get_background(
        path='./assets/bg/session', uuid=uuid,
        default='base', level=stats.level, rank_info=stats.rank_info
    ).convert("RGBA")

    minecraft_16 = ImageFont.truetype('./assets/fonts/minecraft.ttf', 16)

    # Render the stat values
    data = [
        {'position': (87, 131), 'text': f'&a{stats.wins_cum}'},
        {'position': (241, 131), 'text': f'&c{stats.losses_cum}'},
        {'position': (378, 131), 'text': f'&6{stats.wlr_cum}'},
        {'position': (87, 190), 'text': f'&a{stats.final_kills_cum}'},
        {'position': (241, 190), 'text': f'&c{stats.final_deaths_cum}'},
        {'position': (378, 190), 'text': f'&6{stats.fkdr_cum}'},
        {'position': (87, 249), 'text': f'&a{stats.beds_broken_cum}'},
        {'position': (241, 249), 'text': f'&c{stats.beds_lost_cum}'},
        {'position': (378, 249), 'text': f'&6{stats.bblr_cum}'},
        {'position': (87, 308), 'text': f'&a{stats.kills_cum}'},
        {'position': (241, 308), 'text': f'&c{stats.deaths_cum}'},
        {'position': (378, 308), 'text': f'&6{stats.kdr_cum}'},
        {'position': (82, 368), 'text': f'&d{stats.starspd}'},
        {'position': (226, 368), 'text': f'&d{stats.stars_gained}'},
        {'position': (370, 368), 'text': f'&d{stats.games_played_cum:,}'},
        {'position': (82, 427), 'text': f'&d{stats.winspd}'},
        {'position': (226, 427), 'text': f'&d{stats.finalspd}'},
        {'position': (370, 427), 'text': f'&d{stats.bedspd}'},
        {'position': (537, 250), 'text': f'&d# {session}'},
        {'position': (537, 309), 'text': f'&d{stats.total_sessions}'},
        {'position': (537, 368), 'text': f'&d{stats.date_started}'},
        {'position': (537, 427), 'text': f'&d{stats.most_played_cum}'},
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
        rank_info=stats.rank_info,
        image=image,
        font_size=22,
        position=(226, 30),
        align='center'
    )

    render_progress_bar(
        level=stats.level,
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
