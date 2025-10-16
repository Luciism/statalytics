from calc.quests import QuestStats
import statalib as lib
from statalib import HypixelData, to_thread
from statalib.render import ImageRender, BackgroundImageLoader, Prestige


bg = BackgroundImageLoader(dir="quests")

@to_thread
def render_quests(
    name: str,
    uuid: str,
    hypixel_data: HypixelData,
    skin_model: bytes
) -> bytes:
    stats = QuestStats(hypixel_data)

    im = ImageRender(bg.load_background_image(uuid, {
        "level": stats.level, "rank_info": stats.rank_info}))

    # Render the stat values
    im.text.draw_many([
        (Prestige.format_level(stats.questless_star), {'position': (118, 190)}),
        (f'{Prestige.format_level(stats.lvls_daily_win)} '
         f'&f({stats.completions_daily_win:,} Done)', {'position': (118, 249)}),
        (f'{Prestige.format_level(stats.lvls_daily_one_more)} '
         f'&f({stats.completions_daily_one_more:,} Done)', {'position': (118, 308)}),
        (f'{Prestige.format_level(stats.lvls_daily_bed_breaker)} '
         f'&f({stats.completions_daily_bed_breaker:,} Done)', {'position': (118, 367)}),
        (f'{Prestige.format_level(stats.lvls_daily_final_killer)} '
         f'&f({stats.completions_daily_final_killer:,} Done)',
         {'position': (118, 426)}),
        (Prestige.format_level(stats.stars_from_quests), {'position': (332, 190)}),
        (f'{Prestige.format_level(stats.lvls_weekly_bed_elims)} '
         f'&f({stats.completions_weekly_bed_elims:,} Done)',
         {'position': (332, 249)}),
        (f'{Prestige.format_level(stats.lvls_weekly_dream_win)} '
         f'&f({stats.completions_weekly_dream_win:,} Done)',
         {'position': (332, 308)}),
        (f'{Prestige.format_level(stats.lvls_weekly_challenges_win)} '
         f'&f({stats.completions_weekly_challenges_win:,} Done)',
         {'position': (332, 367)}),
        (f'{Prestige.format_level(stats.lvls_weekly_final_killer)} '
         f'&f({stats.completions_weekly_final_killer:,} Done)',
         {'position': (332, 426)}),
        (f'&d{stats.quests_completed:,}', {'position': (536, 249)}),
        (f'&d{stats.formatted_estimated_playtime}', {'position': (536, 308)}),
        (f'&d{stats.questless_hours_per_star:,}', {'position': (536, 367)}),
        (f'&d{stats.hours_per_star:,}', {'position': (536, 426)}),
    ], default_text_options={
        "shadow_offset": (2, 2), "align": "center", "font_size": 16
    })

    im.player.render_hypixel_username(
        name, stats.rank_info, text_options={
        "align": "center",
        "font_size": 22,
        "position": (225, 28)
    })

    lvl_progress, lvl_target, lvl_progress_percent = stats.leveling.progression

    im.progress.draw_progress_bar(
        stats.level,
        progress_percentage=lvl_progress_percent,
        position=(225, 90),
        align="center"
    )
    im.progress.draw_progress_text(
        lvl_progress, lvl_target, position=(225, 121), align="center")

    im.text.draw("Quests Stats", text_options={
        "position": (536, 33),
        "font_size": 17,
        "shadow_offset": (2, 2),
        "align": "center"
    })

    im.player.paste_skin(skin_model, position=(466, 69))

    # Paste overlay image
    im.overlay_image(lib.ASSET_LOADER.load_image("bg/quests/overlay.png"))

    # Save the image
    return im.to_bytes()
