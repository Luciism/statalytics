from calc.total import TotalStats

import statalib as lib
from statalib import to_thread, REL_PATH
from statalib.render import ImageRender, RenderBackground


bg = RenderBackground(dir="total")

@to_thread
def render_total(
    name: str,
    uuid: str,
    mode: str,
    hypixel_data: dict,
    skin_model: bytes,
    save_dir: str
) -> None:
    stats = TotalStats(hypixel_data, mode)

    im = ImageRender(bg.load_background_image(uuid, {
        "level": stats.level, "rank_info": stats.rank_info}))

    # Render the stat values
    im.text.draw_many([
        (f'&a{stats.wins:,}', {'position': (87, 190)}),
        (f'&c{stats.losses:,}', {'position': (241, 190)}),
        (f'&6{stats.wlr:,}', {'position': (378, 190)}),
        (f'&a{stats.final_kills:,}', {'position': (87, 249)}),
        (f'&c{stats.final_deaths:,}', {'position': (241, 249)}),
        (f'&6{stats.fkdr:,}', {'position': (378, 249)}),
        (f'&a{stats.beds_broken:,}', {'position': (87, 308)}),
        (f'&c{stats.beds_lost:,}', {'position': (241, 308)}),
        (f'&6{stats.bblr:,}', {'position': (378, 308)}),
        (f'&a{stats.kills:,}', {'position': (87, 367)}),
        (f'&c{stats.deaths:,}', {'position': (241, 367)}),
        (f'&6{stats.kdr:,}', {'position': (378, 367)}),
        (f'&d{stats.winstreak_str}', {'position': (82, 427)}),
        (f'&d{stats.loot_chests:,}', {'position': (226, 427)}),
        (f'&d{stats.coins:,}', {'position': (370, 427)}),
        (f'&d{stats.games_played:,}', {'position': (537, 250)}),
        (f'&d{stats.most_played}', {'position': (537, 309)}),
        (f'&d{stats.void_deaths:,}', {'position': (537, 368)}),
        (f'&d{stats.items_purchased:,}', {'position': (537, 427)}),
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

    progress, target, lvl_progress_percent = stats.progress

    im.progress.draw_progress_bar(
        stats.level,
        progress_percentage=lvl_progress_percent,
        position=(226, 91),
        align="center"
    )
    im.progress.draw_progress_text(
        progress, target, position=(226, 122), align="center")

    im.player.paste_skin(skin_model, position=(466, 69))

    # Paste overlay image
    im.overlay_image(lib.ASSET_LOADER.load_image("bg/total/overlay_generic.png"))

    # Save the image
    im.save(f'{REL_PATH}/database/rendered/{save_dir}/{mode.lower()}.png')
