from PIL import Image, ImageFont

from calc.total import TotalStats
from statalib import to_thread
from statalib.render import (
    render_display_name,
    get_background,
    paste_skin,
    render_progress_bar,
    render_progress_text,
    render_mc_text
)


@to_thread
def render_total(
    name: str,
    uuid: str,
    mode: str,
    hypixel_data: dict,
    skin_res: bytes,
    save_dir: str,
    method: str
):
    stats = TotalStats(hypixel_data, mode)
    level = stats.level
    rank_info = stats.rank_info

    progress, target, progress_of_10 = stats.progress
    loot_chests, coins = stats.get_chest_and_coins()
    most_played = stats.most_played

    if method == "generic":
        wins, losses, wlr = stats.get_wins()
        final_kills, final_deaths, fkdr = stats.get_finals()
        beds_broken, beds_lost, bblr = stats.get_beds()
        kills, deaths, kdr = stats.get_kills()
        games_played, times_voided, items_purchased,\
            winstreak = stats.get_misc()
    else:
        wins, losses, wlr = stats.get_falling_kills()
        final_kills, final_deaths, fkdr = stats.get_void_kills()
        beds_broken, beds_lost, bblr = stats.get_ranged_kills()
        kills, deaths, kdr = stats.get_fire_kills()
        games_played, times_voided, items_purchased,\
            winstreak = stats.get_misc_pointless()

    image = get_background(
        path='./assets/bg/total', uuid=uuid,
        default='base', level=level, rank_info=rank_info
    ).convert("RGBA")

    minecraft_16 = ImageFont.truetype('./assets/fonts/minecraft.ttf', 16)

    # Render the stat values
    data = [
        {'position': (87, 190), 'text': f'&a{wins}'},
        {'position': (241, 190), 'text': f'&c{losses}'},
        {'position': (378, 190), 'text': f'&6{wlr}'},
        {'position': (87, 249), 'text': f'&a{final_kills}'},
        {'position': (241, 249), 'text': f'&c{final_deaths}'},
        {'position': (378, 249), 'text': f'&6{fkdr}'},
        {'position': (87, 308), 'text': f'&a{beds_broken}'},
        {'position': (241, 308), 'text': f'&c{beds_lost}'},
        {'position': (378, 308), 'text': f'&6{bblr}'},
        {'position': (87, 367), 'text': f'&a{kills}'},
        {'position': (241, 367), 'text': f'&c{deaths}'},
        {'position': (378, 367), 'text': f'&6{kdr}'},
        {'position': (82, 427), 'text': f'&d{winstreak}'},
        {'position': (226, 427), 'text': f'&d{loot_chests}'},
        {'position': (370, 427), 'text': f'&d{coins}'},
        {'position': (537, 250), 'text': f'&d{games_played}'},
        {'position': (537, 309), 'text': f'&d{most_played}'},
        {'position': (537, 368), 'text': f'&d{times_voided}'},
        {'position': (537, 427), 'text': f'&d{items_purchased}'},
        {'position': (537, 46), 'text': f'({mode.title()})'}
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
        position=(226, 31),
        align='center'
    )

    render_progress_bar(
        level=level,
        progress_of_10=progress_of_10,
        position=(226, 91),
        image=image,
        align='center'
    )

    render_progress_text(
        progress=progress,
        target=target,
        position=(226, 122),
        image=image,
        align='center'
    )

    paste_skin(skin_res, image, positions=(466, 69))

    # Paste overlay image
    overlay_image = Image.open(f'./assets/bg/total/overlay_{method}.png')
    overlay_image = overlay_image.convert("RGBA")
    image.paste(overlay_image, (0, 0), overlay_image)

    # Save the image
    image.save(f'./database/rendered/{save_dir}/{mode.lower()}.png')
