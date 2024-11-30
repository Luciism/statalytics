from calc.difference import DifferenceStats
import statalib as lib
from statalib import to_thread, REL_PATH
from statalib.render import ImageRender, BackgroundImageLoader


def color(diff: str) -> tuple:
    if diff[1] == '+':
        return f'&a{diff}'
    return f'&c{diff}'

bg = BackgroundImageLoader(dir="difference")

@to_thread
def render_difference(
    name: str,
    uuid: str,
    relative_date: str,
    method: str,
    mode: str,
    hypixel_data: dict,
    skin_model: bytes,
    save_dir: str
) -> None:
    stats = DifferenceStats(uuid, method, hypixel_data, mode)

    im = ImageRender(bg.load_background_image(
        uuid, {"level": stats.level, "rank_info": stats.rank_info}))

    # Render the stat values
    im.text.draw_many([
        (f'&a{stats.wins_cum}', {'position': (88, 249)}),
        (f'&a{stats.final_kills_cum}', {'position': (88, 309)}),
        (f'&a{stats.beds_broken_cum}', {'position': (88, 369)}),
        (f'&a{stats.kills_cum}', {'position': (88, 429)}),
        (f'&c{stats.losses_cum}', {'position': (242, 249)}),
        (f'&c{stats.final_deaths_cum}', {'position': (242, 309)}),
        (f'&c{stats.beds_lost_cum}', {'position': (242, 369)}),
        (f'&c{stats.deaths_cum}', {'position': (242, 429)}),
        (f'&6{stats.wlr_old} &f➡ &6{stats.wlr_new} {color(stats.wlr_diff)}',
         {'position': (474, 249)}),
        (f'&6{stats.fkdr_old} &f➡ &6{stats.fkdr_new} {color(stats.fkdr_diff)}',
         {'position': (474, 309)}),
        (f'&6{stats.bblr_old} &f➡ &6{stats.bblr_new} {color(stats.bblr_diff)}',
         {'position': (474, 369)}),
        (f'&6{stats.kdr_old} &f➡ &6{stats.kdr_new} {color(stats.kdr_diff)}',
         {'position': (474, 429)}),
        (f"&d{stats.stars_gained}", {'position': (118, 189)}),
        (f"&d{relative_date}", {'position': (332, 189)}),
        (f"({stats.title_mode})", {'position': (536, 46)}),
    ], default_text_options={
        "shadow_offset": (2, 2), "align": "center", "font_size": 16}
    )


    im.player.render_hypixel_username(
        name, stats.rank_info, text_options={
        "align": "center",
        "font_size": 22,
        "position": (225, 26)
    })

    lvl_progress, lvl_target, lvl_progress_percent = stats.leveling.progression

    im.progress.draw_progress_bar(
        stats.level,
        progress_percentage=lvl_progress_percent,
        position=(225, 88),
        align="center"
    )
    im.progress.draw_progress_text(
        lvl_progress, lvl_target, position=(225, 119), align="center")

    im.text.draw(f'{method.title()} Diffs', {
        "position": (536, 25),
        "font_size": 18,
        "shadow_offset": (2, 2),
        "align": "center"
    })

    # Paste overlay image
    im.overlay_image(lib.ASSET_LOADER.load_image("bg/difference/overlay.png"))

    # Render skin
    im.player.paste_skin(skin_model, position=(465, 67))

    # Save the image
    im.save(f'{REL_PATH}/database/rendered/{save_dir}/{mode.lower()}.png')
