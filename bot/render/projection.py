from PIL import Image, ImageFont

from calc.projection import PrestigeStats
from statalib import to_thread, add_suffixes
from statalib.render import (
    get_background,
    paste_skin,
    render_display_name,
    render_mc_text,
    get_formatted_level
)


@to_thread
def render_projection(
    name: str,
    uuid: str,
    session: int,
    mode: str,
    target: int,
    hypixel_data: dict,
    skin_model: bytes,
    save_dir: str
):
    stats = PrestigeStats(uuid, session, target, hypixel_data, mode)

    image = get_background(
        bg_dir='projection', uuid=uuid, level=stats.level, rank_info=stats.rank_info
    ).convert("RGBA")

    minecraft_16 = ImageFont.truetype('./assets/fonts/minecraft.ttf', 16)
    minecraft_18 = ImageFont.truetype('./assets/fonts/minecraft.ttf', 18)
    minecraft_20 = ImageFont.truetype('./assets/fonts/minecraft.ttf', 20)

    # Render the stat values
    data = [
        {'position': (91, 148), 'text': f'&a{add_suffixes(stats.wins_projected)}'},
        {'position': (245, 148), 'text': f'&c{add_suffixes(stats.losses_projected)}'},
        {'position': (382, 148), 'text': f'&6{add_suffixes(stats.wlr_projected)}'},
        {'position': (91, 207), 'text': f'&a{add_suffixes(stats.final_kills_projected)}'},
        {'position': (245, 207), 'text': f'&c{add_suffixes(stats.final_deaths_projected)}'},
        {'position': (382, 207), 'text': f'&6{add_suffixes(stats.fkdr_projected)}'},
        {'position': (91, 266), 'text': f'&a{add_suffixes(stats.beds_broken_projected)}'},
        {'position': (245, 266), 'text': f'&c{add_suffixes(stats.beds_lost_projected)}'},
        {'position': (382, 266), 'text': f'&6{add_suffixes(stats.bblr_projected)}'},
        {'position': (91, 325), 'text': f'&a{add_suffixes(stats.kills_projected)}'},
        {'position': (245, 325), 'text': f'&c{add_suffixes(stats.deaths_projected)}'},
        {'position': (382, 325), 'text': f'&6{add_suffixes(stats.kdr_projected)}'},
        {'position': (87, 385), 'text': f'&d{add_suffixes(stats.wins_per_star)}'},
        {'position': (230, 385), 'text': f'&d{add_suffixes(stats.final_kills_per_star)}'},
        {'position': (374, 385), 'text': f'&d{add_suffixes(stats.beds_broken_per_star)}'},
        {'position': (537, 250), 'text': f'&d{stats.complete_percent}'},
        {'position': (537, 309), 'text': f'&d{add_suffixes(stats.levels_to_go)}'},
        {'position': (537, 368), 'text': f'&d{add_suffixes(stats.levels_per_day)}'},
        {'position': (537, 427), 'text': f'&d{add_suffixes(stats.items_purchased_projected)}'},
        {'position': (537, 46), 'text': f'({stats.title_mode})'}
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
        position=(226, 28),
        align='center'
    )

    render_mc_text(
        text=f'Projected to hit on: &d{stats.projection_date}',
        position=(229, 425),
        font=minecraft_18,
        image=image,
        shadow_offset=(2, 2),
        align='center'
    )

    # Render progress to target
    formatted_lvl = get_formatted_level(stats.level)
    formatted_target = get_formatted_level(target)

    render_mc_text(
        text=f'{formatted_lvl} &f/ {formatted_target}',
        position=(226, 84),
        font=minecraft_20,
        image=image,
        shadow_offset=(2, 2),
        align='center'
    )

    paste_skin(skin_model, image, positions=(466, 69))

    # Paste overlay image
    overlay_image = Image.open('./assets/bg/projection/overlay.png')
    overlay_image = overlay_image.convert('RGBA')
    image.paste(overlay_image, (0, 0), overlay_image)

    # Save the image
    image.save(f'./database/rendered/{save_dir}/{mode.lower()}.png')
    if mode.lower() == "overall":
        return stats.level
