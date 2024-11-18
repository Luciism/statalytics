from calc.rotational import RotationalStats, HistoricalRotationalStats

import statalib as lib
from statalib import rotational_stats as rotational, to_thread, REL_PATH
from statalib.render import ImageRender, RenderBackground


@to_thread
def render_rotational(
    name: str,
    uuid: str,
    tracker: str,
    relative_date: str,
    title: str,
    mode: str,
    hypixel_data: dict,
    skin_model: bytes,
    save_dir: str,
    period_id: rotational.HistoricalRotationPeriodID | None=None
) -> None:
    if tracker in rotational.RotationType._value2member_map_:
        rotation_type = rotational.RotationType.from_string(tracker)
        stats = RotationalStats(uuid, rotation_type, hypixel_data, mode)
    else:
        stats = HistoricalRotationalStats(uuid, period_id, hypixel_data, mode)

    bg = RenderBackground(dir=f'rotational/{tracker}')
    im = ImageRender(bg.load_background_image(uuid, {
        "level": stats.level, "rank_info": stats.rank_info}))

    # Render the stat values
    im.text.draw_many([
        (f'&a{stats.wins_cum:,}', {'position': (87, 190)}),
        (f'&c{stats.losses_cum:,}', {'position': (241, 190)}),
        (f'&6{stats.wlr_cum:,}', {'position': (378, 190)}),
        (f'&a{stats.final_kills_cum:,}', {'position': (87, 249)}),
        (f'&c{stats.final_deaths_cum:,}', {'position': (241, 249)}),
        (f'&6{stats.fkdr_cum:,}', {'position': (378, 249)}),
        (f'&a{stats.beds_broken_cum:,}', {'position': (87, 308)}),
        (f'&c{stats.beds_lost_cum:,}', {'position': (241, 308)}),
        (f'&6{stats.bblr_cum:,}', {'position': (378, 308)}),
        (f'&a{stats.kills_cum:,}', {'position': (87, 367)}),
        (f'&c{stats.deaths_cum:,}', {'position': (241, 367)}),
        (f'&6{stats.kdr_cum:,}', {'position': (378, 367)}),
        (f'&d{stats.stars_gained}', {'position': (82, 427)}),
        (f'&d{stats.timezone}', {'position': (226, 427)}),
        (f'&d{stats.reset_time}', {'position': (370, 427)}),
        (f'&d{stats.games_played_cum:,}', {'position': (537, 249)}),
        (f'&d{stats.most_played_cum}', {'position': (537, 308)}),
        (f'&d{relative_date}', {'position': (537, 367)}),
        (f'&d{stats.items_purchased_cum:,}', {'position': (537, 427)}),
        (f'({stats.title_mode})', {'position': (537, 46)}),
    ], default_text_options={
        "shadow_offset": (2, 2), "align": "center", "font_size": 16
    })

    im.player.render_hypixel_username(
        name, stats.rank_info, text_options={
        "align": "center",
        "font_size": 22,
        "position": (226, 31)
    })

    lvl_progress, lvl_target, lvl_progress_percent = stats.leveling.progression

    im.progress.draw_progress_bar(
        stats.level,
        progress_percentage=lvl_progress_percent,
        position=(226, 91),
        align="center"
    )
    im.progress.draw_progress_text(
        lvl_progress, lvl_target, position=(226, 122), align="center")

    im.text.draw(title, text_options={
        "position": (537, 27),
        "font_size": 17,
        "shadow_offset": (2, 2),
        "align": "center"
    })

    # Paste skin
    im.player.paste_skin(skin_model, position=(466, 69))

    # Paste overlay
    im.overlay_image(lib.ASSET_LOADER.load_image("bg/rotational/overlay.png"))

    # Save the image
    im.save(f'{REL_PATH}/database/rendered/{save_dir}/{mode.lower()}.png')
