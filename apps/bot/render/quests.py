from PIL import Image, ImageFont

from calc.quests import QuestStats
from statalib import to_thread, REL_PATH
from statalib.render import (
    render_display_name,
    get_background,
    paste_skin,
    render_progress_bar,
    render_progress_text,
    render_mc_text,
    image_to_bytes,
    get_formatted_level
)


@to_thread
def render_quests(
    name: str,
    uuid: str,
    hypixel_data: dict,
    skin_model: bytes
):
    stats = QuestStats(hypixel_data)
    progress, target, progress_of_10 = stats.progress

    image = get_background(
        bg_dir='quests', uuid=uuid, level=stats.stars, rank_info=stats.rank_info
    ).convert("RGBA")

    minecraft_16 = ImageFont.truetype(f'{REL_PATH}/assets/fonts/minecraft.ttf', 16)

    # Render the stat values
    data = [
        {
        'position': (118, 190),
        'text': get_formatted_level(stats.questless_star)},
        {
        'position': (118, 249),
        'text': f'{get_formatted_level(stats.lvls_daily_win)} '
                f'&f({stats.completions_daily_win:,} Done)'},
        {
        'position': (118, 308),
        'text': f'{get_formatted_level(stats.lvls_daily_one_more)} '
                f'&f({stats.completions_daily_one_more:,} Done)'},
        {
        'position': (118, 367),
        'text': f'{get_formatted_level(stats.lvls_daily_bed_breaker)} '
                f'&f({stats.completions_daily_bed_breaker:,} Done)'},
        {
        'position': (118, 426),
        'text': f'{get_formatted_level(stats.lvls_daily_final_killer)} '
                f'&f({stats.completions_daily_final_killer:,} Done)'},
        {
        'position': (332, 190),
        'text': get_formatted_level(stats.stars_from_quests)},
        {
        'position': (332, 249),
        'text': f'{get_formatted_level(stats.lvls_weekly_bed_elims)} '
                f'&f({stats.completions_weekly_bed_elims:,} Done)'},
        {
        'position': (332, 308),
        'text': f'{get_formatted_level(stats.lvls_weekly_dream_win)} '
                f'&f({stats.completions_weekly_dream_win:,} Done)'},
        {
        'position': (332, 367),
        'text': f'{get_formatted_level(stats.lvls_weekly_challenges_win)} '
                f'&f({stats.completions_weekly_challenges_win:,} Done)'},
        {
        'position': (332, 426),
        'text': f'{get_formatted_level(stats.lvls_weekly_final_killer)} '
                f'&f({stats.completions_weekly_final_killer:,} Done)'},

        {'position': (536, 249), 'text': f'&d{stats.quests_completed:,}'},
        {'position': (536, 308), 'text': f'&d{stats.formatted_estimated_playtime}'},
        {'position': (536, 367), 'text': f'&d{stats.questless_hours_per_star:,}'},
        {'position': (536, 426), 'text': f'&d{stats.hours_per_star:,}'},
    ]

    for values in data:
        render_mc_text(
            image=image,
            shadow_offset=(2, 2),
            font=minecraft_16,
            align='center',
            **values
        )

    render_display_name(
        username=name,
        rank_info=stats.rank_info,
        image=image,
        font_size=22,
        position=(225, 28),
        align='center'
    )

    render_progress_bar(
        level=stats.stars,
        progress_of_10=progress_of_10,
        position=(225, 90),
        image=image,
        align='center'
    )

    render_progress_text(
        progress=progress,
        target=target,
        position=(225, 121),
        image=image,
        align='center'
    )

    render_mc_text(
        text="Quests Stats",
        position=(536, 33),
        font_size=17,
        image=image,
        shadow_offset=(2, 2),
        align='center'
    )


    paste_skin(skin_model, image, positions=(466, 69))

    # Paste overlay image
    overlay_image = Image.open(f'{REL_PATH}/assets/bg/quests/overlay.png')
    overlay_image = overlay_image.convert("RGBA")
    image.paste(overlay_image, (0, 0), overlay_image)

    # Save the image
    return image_to_bytes(image)
