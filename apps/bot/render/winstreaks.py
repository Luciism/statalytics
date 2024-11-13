from calc.winstreaks import WinstreakStats

import statalib as lib
from statalib import to_thread
from statalib.render import ImageRender, RenderBackground


bg = RenderBackground(dir="winstreaks")

@to_thread
def render_winstreaks(
    name: str,
    uuid: str,
    hypixel_data: dict,
    skin_model: bytes
) -> bytes:
    stats = WinstreakStats(hypixel_data)

    im = ImageRender(bg.load_background_image(uuid, {
        "level": stats.level, "rank_info": stats.rank_info}))

    # Render the stat values
    im.text.draw_many([
        (f'&a{stats.winstreak_overall}', {'position': (118, 190)}),
        (f'&a{stats.winstreak_solos}', {'position': (333, 190)}),
        (f'&a{stats.winstreak_doubles}', {'position': (118, 249)}),
        (f'&a{stats.winstreak_threes}', {'position': (333, 249)}),
        (f'&a{stats.winstreak_fours}', {'position': (118, 308)}),
        (f'&a{stats.winstreak_4v4}', {'position': (333, 308)}),
        (f'&d{stats.wins:,}', {'position': (537, 249)}),
        (f'&d{stats.api_status}', {'position': (537, 308)}),
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

    im.player.paste_skin(skin_model, position=(466, 69))

    im.overlay_image(lib.ASSET_LOADER.load_image("bg/winstreaks/overlay.png"))

    return im.to_bytes()
