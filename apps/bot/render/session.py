from calc.session import SessionStats

import statalib as lib
from statalib import to_thread, REL_PATH
from statalib.sessions import BedwarsSession
from statalib.render import ImageRender, RenderBackground


bg = RenderBackground(dir="session")

@to_thread
def render_session(
    name: str,
    uuid: str,
    session_info: BedwarsSession,
    mode: str,
    hypixel_data: dict,
    skin_model: bytes,
    save_dir: str
) -> None:
    stats = SessionStats(uuid, session_info, hypixel_data, mode)

    im = ImageRender(bg.load_background_image(uuid, {
        "level": stats.level, "rank_info": stats.rank_info}))

    # Render the stat values
    im.text.draw_many([
        (f'&a{stats.wins_cum:,}', {'position': (87, 131)}),
        (f'&c{stats.losses_cum:,}', {'position': (241, 131)}),
        (f'&6{stats.wlr_cum:,}', {'position': (378, 131)}),
        (f'&a{stats.final_kills_cum:,}', {'position': (87, 190)}),
        (f'&c{stats.final_deaths_cum:,}', {'position': (241, 190)}),
        (f'&6{stats.fkdr_cum:,}', {'position': (378, 190)}),
        (f'&a{stats.beds_broken_cum:,}', {'position': (87, 249)}),
        (f'&c{stats.beds_lost_cum:,}', {'position': (241, 249)}),
        (f'&6{stats.bblr_cum:,}', {'position': (378, 249)}),
        (f'&a{stats.kills_cum:,}', {'position': (87, 308)}),
        (f'&c{stats.deaths_cum:,}', {'position': (241, 308)}),
        (f'&6{stats.kdr_cum:,}', {'position': (378, 308)}),
        (f'&d{stats.starspd}', {'position': (82, 368)}),
        (f'&d{stats.stars_gained}', {'position': (226, 368)}),
        (f'&d{stats.games_played_cum:,}', {'position': (370, 368)}),
        (f'&d{stats.winspd}', {'position': (82, 427)}),
        (f'&d{stats.finalspd}', {'position': (226, 427)}),
        (f'&d{stats.bedspd}', {'position': (370, 427)}),
        (f'&d# {session_info.session_id}', {'position': (537, 250)}),
        (f'&d{stats.total_sessions}', {'position': (537, 309)}),
        (f'&d{stats.date_started}', {'position': (537, 368)}),
        (f'&d{stats.most_played_cum}', {'position': (537, 427)}),
        (f'({stats.title_mode})', {'position': (537, 46)}),
    ], default_text_options={
        "shadow_offset": (2, 2), "align": "center", "font_size": 16
    })

    im.player.render_hypixel_username(
        name, stats.rank_info, text_options={
        "align": "center",
        "font_size": 22,
        "position": (226, 30)
    })

    im.progress.draw_progress_bar(
        stats.level,
        progress_percentage=stats.leveling.progression.progress_percent,
        position=(226, 61),
        align="center"
    )

    im.text.draw("Session Stats", text_options={
        "position": (537, 27),
        "font_size": 17,
        "shadow_offset": (2, 2),
        "align": "center"
    })

    im.player.paste_skin(skin_model, position=(466, 69))

    # Paste overlay image
    im.overlay_image(lib.ASSET_LOADER.load_image("bg/session/overlay.png"))

    # Save the image
    im.save(f'{REL_PATH}/database/rendered/{save_dir}/{mode.lower()}.png')
