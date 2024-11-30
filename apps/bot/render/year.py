from calc.year import YearStats

import statalib as lib
from statalib import BedwarsSession
from statalib.hypixel import add_suffixes
from statalib.render import ImageRender, BackgroundImageLoader, Prestige


bg = BackgroundImageLoader(dir="year")

@lib.to_thread
def render_year(
    name: str,
    uuid: str,
    session_info: BedwarsSession,
    year: int,
    mode: str,
    hypixel_data: dict,
    skin_model: bytes,
    save_dir: str
) -> None:
    stats = YearStats(uuid, session_info, year, hypixel_data, mode)

    im = ImageRender(bg.load_background_image(uuid, {
        "level": stats.level, "rank_info": stats.rank_info}))

    # Render the stat values
    im.text.draw_many([
        (f'&a{add_suffixes(stats.wins_projected)}', {'position': (91, 148)}),
        (f'&c{add_suffixes(stats.losses_projected)}', {'position': (245, 148)}),
        (f'&6{add_suffixes(stats.wlr_projected)}', {'position': (382, 148)}),
        (f'&a{add_suffixes(stats.final_kills_projected)}', {'position': (91, 207)}),
        (f'&c{add_suffixes(stats.final_deaths_projected)}', {'position': (245, 207)}),
        (f'&6{add_suffixes(stats.fkdr_projected)}', {'position': (382, 207)}),
        (f'&a{add_suffixes(stats.beds_broken_projected)}', {'position': (91, 266)}),
        (f'&c{add_suffixes(stats.beds_lost_projected)}', {'position': (245, 266)}),
        (f'&6{add_suffixes(stats.bblr_projected)}', {'position': (382, 266)}),
        (f'&a{add_suffixes(stats.kills_projected)}', {'position': (91, 325)}),
        (f'&c{add_suffixes(stats.deaths_projected)}', {'position': (245, 325)}),
        (f'&6{add_suffixes(stats.kdr_projected)}', {'position': (382, 325)}),
        (f'&d{add_suffixes(stats.wins_per_star)}', {'position': (87, 385)}),
        (f'&d{add_suffixes(stats.final_kills_per_star)}', {'position': (230, 385)}),
        (f'&d{add_suffixes(stats.beds_broken_per_star)}', {'position': (374, 385)}),
        (f'&d{stats.complete_percent}', {'position': (537, 250)}),
        (f'&d{add_suffixes(stats.days_to_go)}', {'position': (537, 309)}),
        (f'&d{add_suffixes(stats.levels_per_day)}', {'position': (537, 368)}),
        (f'&d{add_suffixes(stats.items_purchased_projected)}', {'position': (537, 427)}),
        (f'({stats.title_mode})', {'position': (537, 46)}),
    ], default_text_options={
        "shadow_offset": (2, 2), "align": "center", "font_size": 16
    })

    im.player.render_hypixel_username(
        name, stats.rank_info, text_options={
        "align": "center",
        "font_size": 22,
        "position": (226, 28)
    })

    im.text.draw(f"&fPredictions For Year: &d{year}", text_options={
        "position": (229, 425),
        "font_size": 18,
        "shadow_offset": (2, 2),
        "align": "center"
    })

    # Render progress to target
    formatted_lvl = Prestige.format_level(stats.level)
    formatted_target = Prestige.format_level(int(stats.target_level))

    im.text.draw(f"{formatted_lvl} &f/ {formatted_target}", {
        "position": (226, 84),
        "font_size": 20,
        "shadow_offset": (2, 2),
        "align": "center"
    })

    im.text.draw(f"Year {year}", {
        "position": (537, 27),
        "font_size": 18,
        "shadow_offset": (2, 2),
        "align": "center"
    })

    im.player.paste_skin(skin_model, position=(466, 69))

    # Paste overlay
    im.overlay_image(lib.ASSET_LOADER.load_image("bg/year/overlay.png"))

    # Save the image
    im.save(f'{lib.REL_PATH}/database/rendered/{save_dir}/{mode.lower()}.png')

    if mode.lower() == "overall":
        return stats.level
