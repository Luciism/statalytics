from calc.projection import PrestigeStats

import statalib as lib
from statalib import to_thread, REL_PATH, BedwarsSession
from statalib.hypixel import add_suffixes
from statalib.render import ImageRender, BackgroundImageLoader, Prestige


bg = BackgroundImageLoader(dir="projection")

@to_thread
def render_projection(
    name: str,
    uuid: str,
    session_info: BedwarsSession,
    mode: str,
    target: int,
    hypixel_data: dict,
    skin_model: bytes,
    save_dir: str
) -> None | int:
    stats = PrestigeStats(session_info, target, hypixel_data, mode)

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
        (f'&d{add_suffixes(stats.levels_to_go)}', {'position': (537, 309)}),
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

    im.text.draw(f'Projected to hit on: &d{stats.projection_date}', {
        "position": (229, 425),
        "font_size": 18,
        "shadow_offset": (2, 2),
        "align": "center"
    })

    # Render progress to target
    formatted_lvl = Prestige(stats.level).formatted_level
    formatted_target = Prestige(target).formatted_level

    im.text.draw(f'{formatted_lvl} &f/ {formatted_target}', {
        "position": (226, 84),
        "font_size": 20,
        "shadow_offset": (2, 2),
        "align": "center"
    })

    im.player.paste_skin(skin_model, position=(466, 69))

    # Paste overlay image
    im.overlay_image(lib.ASSET_LOADER.load_image("bg/projection/overlay.png"))

    # Save the image
    im.save(f'{REL_PATH}/database/rendered/{save_dir}/{mode.lower()}.png')

    if mode.lower() == "overall":
        return stats.level
