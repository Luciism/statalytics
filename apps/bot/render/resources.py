from calc.resources import ResourcesStats
import statalib as lib
from statalib import to_thread, REL_PATH
from statalib.render import ImageRender, BackgroundImageLoader


bg = BackgroundImageLoader(dir="resources")

@to_thread
def render_resources(
    name: str,
    uuid: str,
    mode: str,
    hypixel_data: dict,
    save_dir: str
) -> None:
    stats = ResourcesStats(hypixel_data, mode)

    level = stats.level

    rank_info = stats.rank_info

    iron_per_game, gold_per_game, dias_per_game,\
        ems_per_game = stats.get_per_game()

    iron_per_star, gold_per_star, dias_per_star,\
        ems_per_star = stats.get_per_star()

    iron_percent, gold_percent, dia_percent,\
        em_percent = stats.get_percentages()

    iron_most_mode, gold_most_mode, dia_most_mode,\
        em_most_mode = stats.get_most_modes()

    im = ImageRender(bg.load_background_image(uuid, {
        "level": stats.level, "rank_info": stats.rank_info}))

    # Render the stat values
    im.text.draw_many([
        (f'&f{stats.iron_collected:,}', {'position': (89, 189)}),
        (f'&6{stats.gold_collected:,}', {'position': (244, 189)}),
        (f'&b{stats.diamonds_collected:,}', {'position': (399, 189)}),
        (f'&a{stats.emeralds_collected:,}', {'position': (553, 189)}),
        (f'&f{iron_per_game}', {'position': (89, 249)}),
        (f'&6{gold_per_game}', {'position': (244, 249)}),
        (f'&b{dias_per_game}', {'position': (399, 249)}),
        (f'&a{ems_per_game}', {'position': (553, 249)}),
        (f'&f{iron_per_star}', {'position': (89, 309)}),
        (f'&6{gold_per_star}', {'position': (244, 309)}),
        (f'&b{dias_per_star}', {'position': (399, 309)}),
        (f'&a{ems_per_star}', {'position': (553, 309)}),
        (f'&f{iron_percent}', {'position': (89, 369)}),
        (f'&6{gold_percent}', {'position': (244, 369)}),
        (f'&b{dia_percent}', {'position': (399, 369)}),
        (f'&a{em_percent}', {'position': (553, 369)}),
        (f'&f{iron_most_mode}', {'position': (89, 429)}),
        (f'&6{gold_most_mode}', {'position': (244, 429)}),
        (f'&b{dia_most_mode}', {'position': (399, 429)}),
        (f'&a{em_most_mode}', {'position': (553, 429)}),
        (f'&d{stats.resources_collected:,}', {'position': (537, 129)}),
        (f'({stats.title_mode})', {'position': (537, 65)}),
    ], default_text_options={
        "shadow_offset": (2, 2), "align": "center", "font_size": 16
    })

    im.player.render_hypixel_username(
        name, stats.rank_info, text_options={
        "align": "center",
        "font_size": 22,
        "position": (226, 27)
    })

    lvl_progress, lvl_target, lvl_progress_percent = stats.leveling.progression

    im.progress.draw_progress_bar(
        stats.level,
        progress_percentage=lvl_progress_percent,
        position=(226, 88),
        align="center"
    )
    im.progress.draw_progress_text(
        lvl_progress, lvl_target, position=(226, 119), align="center")

    # Paste overlay image
    im.overlay_image(lib.ASSET_LOADER.load_image("bg/resources/overlay.png"))

    # Save the image
    im.save(f'{REL_PATH}/database/rendered/{save_dir}/{mode.lower()}.png')
