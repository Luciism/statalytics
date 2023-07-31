from PIL import Image, ImageFont

from calc.average import Ratios
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
def render_average(
    name: str,
    uuid: str,
    mode: str,
    hypixel_data: dict,
    skin_res: bytes,
    save_dir: str
):
    ratios = Ratios(hypixel_data, mode)
    level = ratios.level
    rank_info = ratios.rank_info
    progress, target, progress_of_10 = ratios.progress

    (
        wins_per_star,
        final_kills_per_star,
        beds_broken_per_star,
        kills_per_star,
        losses_per_star,
        final_deaths_per_star,
        beds_lost_per_star,
        deaths_per_star
    ) = ratios.get_per_star()

    (
        final_kills_per_game,
        beds_broken_per_game,
        kills_per_game,
        games_per_final_death,
        games_per_bed_lost,
        deaths_per_game,
    ) = ratios.get_per_game()


    clutch_rate = ratios.get_clutch_rate()
    win_rate = ratios.get_win_rate()
    loss_rate = ratios.get_loss_rate()

    most_wins = ratios.get_most_wins()
    most_losses = ratios.get_most_losses()


    image = get_background(
        path='./assets/bg/average', uuid=uuid,
        default='base', level=level, rank_info=rank_info
    ).convert("RGBA")

    minecraft_16 = ImageFont.truetype('./assets/fonts/minecraft.ttf', 16)
    minecraft_18 = ImageFont.truetype('./assets/fonts/minecraft.ttf', 18)

    # Render the stat values
    data = [
        {'position': (88, 249), 'text': f'&a{wins_per_star}'},
        {'position': (88, 309), 'text': f'&a{final_kills_per_star}'},
        {'position': (88, 369), 'text': f'&a{beds_broken_per_star}'},
        {'position': (88, 429), 'text': f'&a{kills_per_star}'},

        {'position': (242, 249), 'text': f'&c{losses_per_star}'},
        {'position': (242, 309), 'text': f'&c{final_deaths_per_star}'},
        {'position': (242, 369), 'text': f'&c{beds_lost_per_star}'},
        {'position': (242, 429), 'text': f'&c{deaths_per_star}'},

        {'position': (396, 249), 'text': f'&a{most_wins}'},
        {'position': (396, 309), 'text': f'&a{final_kills_per_game}'},
        {'position': (396, 369), 'text': f'&a{beds_broken_per_game}'},
        {'position': (396, 429), 'text': f'&a{kills_per_game}'},

        {'position': (551, 249), 'text': f'&c{most_losses}'},
        {'position': (551, 309), 'text': f'&c{games_per_final_death}'},
        {'position': (551, 369), 'text': f'&c{games_per_bed_lost}'},
        {'position': (551, 429), 'text': f'&c{deaths_per_game}'},

        {'position': (83, 189), 'text': f'&a{clutch_rate}'},
        {'position': (225, 189), 'text': f'&a{win_rate}'},
        {'position': (368, 189), 'text': f'&c{loss_rate}'},

        {'position': (536, 46), 'text': f'&f({mode.title()})'}
    ]

    for values in data:
        render_mc_text(
            image=image,
            shadow_offset=(2, 2),
            align='center',
            font=minecraft_16,
            **values
        )

    render_display_name(
        username=name,
        rank_info=rank_info,
        image=image,
        font_size=22,
        position=(225, 26),
        align='center'
    )

    render_progress_bar(
        level=level,
        progress_of_10=progress_of_10,
        position=(225, 88),
        image=image,
        align='center'
    )

    render_progress_text(
        progress=progress,
        target=target,
        position=(225, 119),
        image=image,
        align='center'
    )

    render_mc_text(
        text='Average Stats',
        position=(536, 25),
        font=minecraft_18,
        image=image,
        shadow_offset=(2, 2),
        align='center'
    )

    # Paste overlay image
    overlay_image = Image.open(
        './assets/bg/average/overlay.png').convert("RGBA")

    image.paste(overlay_image, (0, 0), overlay_image)

    # Render skin
    paste_skin(skin_res, image, positions=(465, 67))

    # Save the image
    image.save(f'./database/rendered/{save_dir}/{mode.lower()}.png')
