from calc.average import AverageStats
import statalib as lib
from statalib import HypixelData, Mode, to_thread, REL_PATH
from statalib.render import ImageRender, BackgroundImageLoader


bg = BackgroundImageLoader(dir="average")

@to_thread
def render_average(
    name: str,
    uuid: str,
    mode: Mode,
    hypixel_data: HypixelData,
    skin_model: bytes,
    save_dir: str
) -> None:
    stats = AverageStats(hypixel_data, mode)

    im = ImageRender(bg.load_background_image(uuid, {
        "level": stats.level, "rank_info": stats.rank_info}))

    # Render the stat values
    im.text.draw_many([
        (f"&a{stats.wins_per_star}", {"position": (88, 249)}),
        (f"&a{stats.final_kills_per_star}", {"position": (88, 309)}),
        (f"&a{stats.beds_broken_per_star}", {"position": (88, 369)}),
        (f"&a{stats.kills_per_star}", {"position": (88, 429)}),
        (f"&c{stats.losses_per_star}", {"position": (242, 249)}),
        (f"&c{stats.final_deaths_per_star}", {"position": (242, 309)}),
        (f"&c{stats.beds_lost_per_star}", {"position": (242, 369)}),
        (f"&c{stats.deaths_per_star}", {"position": (242, 429)}),
        (f"&a{stats.most_wins_mode}", {"position": (396, 249)}),
        (f"&a{stats.final_kills_per_game}", {"position": (396, 309)}),
        (f"&a{stats.beds_broken_per_game}", {"position": (396, 369)}),
        (f"&a{stats.kills_per_game}", {"position": (396, 429)}),
        (f"&c{stats.most_losses_mode}", {"position": (551, 249)}),
        (f"&c{stats.games_per_final_death}", {"position": (551, 309)}),
        (f"&c{stats.games_per_bed_lost}", {"position": (551, 369)}),
        (f"&c{stats.deaths_per_game}", {"position": (551, 429)}),
        (f"&a{stats.clutch_rate}", {"position": (83, 189)}),
        (f"&a{stats.win_rate}", {"position": (225, 189)}),
        (f"&c{stats.loss_rate}", {"position": (368, 189)}),
        (f"&f({stats.title_mode})", {"position": (536, 46)}),
    ], default_text_options={
        "shadow_offset": (2, 2), "align": "center", "font_size": 16
    })

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

    im.text.draw("Avg Stats", text_options={
        "position": (536, 25),
        "font_size": 18,
        "shadow_offset": (2, 2),
        "align": "center"
    })

    # Paste overlay image
    im.overlay_image(lib.ASSET_LOADER.load_image("bg/average/overlay.png"))

    # Render skin
    im.player.paste_skin(skin_model, position=(465, 67))

    # Save the image
    im.save(f'{REL_PATH}/database/rendered/{save_dir}/{mode.id}.png')
