from PIL import Image, ImageFont

from calc.year import YearStats
from statalib import to_thread
from statalib.render import (
    get_background,
    paste_skin,
    render_display_name,
    render_mc_text,
    get_formatted_level
)


@to_thread
def render_year(
    name: str,
    uuid: str,
    session: int,
    year: int,
    mode: str,
    hypixel_data: dict,
    skin_res: bytes,
    save_dir: str
):
    stats = YearStats(uuid, session, year, hypixel_data, mode)

    level = int(stats.level_hypixel)
    target = stats.get_target()

    rank_info = stats.rank_info

    days_to_go = str(stats.days_to_go)
    stars_per_day = f'{round(stats.stars_per_day, 2):,}'
    complete_percent = stats.complete_percentage

    items_purchased = stats.get_items_purchased()

    kills, deaths, kdr = stats.get_kills()
    final_kills, final_deaths, fkdr = stats.get_finals()
    beds_broken, beds_lost, bblr = stats.get_beds()
    wins, losses, wlr = stats.get_wins()
    wins_per_star, finals_per_star, beds_per_star = stats.get_per_star()
    year = str(year)

    image = get_background(
        path='./assets/bg/year', uuid=uuid,
        default='base', level=level, rank_info=rank_info
    ).convert("RGBA")

    minecraft_16 = ImageFont.truetype('./assets/fonts/minecraft.ttf', 16)
    minecraft_18 = ImageFont.truetype('./assets/fonts/minecraft.ttf', 18)
    minecraft_20 = ImageFont.truetype('./assets/fonts/minecraft.ttf', 20)

    # Render the stat values
    data = [
        {'position': (91, 148), 'text': f'&a{wins}'},
        {'position': (245, 148), 'text': f'&c{losses}'},
        {'position': (382, 148), 'text': f'&6{wlr}'},
        {'position': (91, 207), 'text': f'&a{final_kills}'},
        {'position': (245, 207), 'text': f'&c{final_deaths}'},
        {'position': (382, 207), 'text': f'&6{fkdr}'},
        {'position': (91, 266), 'text': f'&a{beds_broken}'},
        {'position': (245, 266), 'text': f'&c{beds_lost}'},
        {'position': (382, 266), 'text': f'&6{bblr}'},
        {'position': (91, 325), 'text': f'&a{kills}'},
        {'position': (245, 325), 'text': f'&c{deaths}'},
        {'position': (382, 325), 'text': f'&6{kdr}'},
        {'position': (87, 385), 'text': f'&d{wins_per_star}'},
        {'position': (231, 385), 'text': f'&d{finals_per_star}'},
        {'position': (374, 385), 'text': f'&d{beds_per_star}'},
        {'position': (537, 250), 'text': f'&d{complete_percent}'},
        {'position': (537, 309), 'text': f'&d{days_to_go}'},
        {'position': (537, 368), 'text': f'&d{stars_per_day}'},
        {'position': (537, 427), 'text': f'&d{items_purchased}'},
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
        rank_info=rank_info,
        image=image,
        font_size=22,
        position=(226, 28),
        align='center'
    )

    render_mc_text(
        text=f'&fPredictions For Year: &d{year}',
        position=(229, 425),
        font=minecraft_18,
        image=image,
        shadow_offset=(2, 2),
        align='center'
    )

    # Render progress to target
    formatted_lvl = get_formatted_level(level)
    formatted_target = get_formatted_level(target)

    render_mc_text(
        text=f'{formatted_lvl} &f/ {formatted_target}',
        position=(226, 84),
        font=minecraft_20,
        image=image,
        shadow_offset=(2, 2),
        align='center'
    )

    render_mc_text(
        text=f'Year {year}',
        position=(537, 27),
        font=minecraft_18,
        image=image,
        shadow_offset=(2, 2),
        align='center'
    )

    paste_skin(skin_res, image, positions=(466, 69))

    # Paste overlay
    overlay_image = Image.open('./assets/bg/year/overlay.png')
    overlay_image = overlay_image.convert('RGBA')
    image.paste(overlay_image, (0, 0), overlay_image)

    # Save the image
    image.save(f'./database/rendered/{save_dir}/{mode.lower()}.png')
    if mode.lower() == "overall":
        return level
