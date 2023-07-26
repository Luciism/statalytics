from PIL import ImageFont

from calc.milestones import Stats
from statalib import to_thread
from statalib.render import (
    render_display_name,
    get_background,
    paste_skin,
    render_progress_bar,
    render_progress_text,
    render_mc_text,
    get_formatted_level
)


@to_thread
def render_milestones(
    name: str,
    uuid: str,
    mode: str,
    session: int,
    hypixel_data: dict,
    skin_res: bytes,
    save_dir: str
):
    stats = Stats(name, uuid, mode, session, hypixel_data)

    level = stats.level
    rank_info = stats.rank_info

    stars_until_value, stars_until_target = stats.get_stars()
    progress, target, progress_of_10 = stats.progress

    wins_until_wlr, wins_at_wlr, target_wlr, wins_until_wins,\
        target_wins, losses_until_losses, target_losses = stats.get_wins()

    final_kills_until_fkdr, final_kills_at_fkdr, target_fkdr,\
        final_kills_until_final_kills, target_final_kills,\
        final_deaths_until_final_deaths, target_final_deaths = stats.get_finals()

    beds_broken_until_bblr, beds_broken_at_bblr, target_bblr,\
        beds_broken_until_beds_broken, target_beds_broken,\
        beds_lost_until_beds_lost, target_beds_lost = stats.get_beds()

    kills_until_kdr, kills_at_kdr, target_kdr, kills_until_kills,\
        target_kills, deaths_until_deaths, target_deaths = stats.get_kills()

    image = get_background(
        path='./assets/bg/milestones', uuid=uuid,
        default='base', level=level, rank_info=rank_info
    ).convert("RGBA")

    minecraft_16 = ImageFont.truetype('./assets/fonts/minecraft.ttf', 16)
    minecraft_18 = ImageFont.truetype('./assets/fonts/minecraft.ttf', 18)

    # Render the stat values
    data = [
        {'position': (31, 212),
         'text': f'&a{wins_until_wlr} &fWins Until &6{target_wlr}'},
        {'position': (31, 241),
         'text': f'&a{wins_at_wlr} &fWins At &6{target_wlr}'},
        {'position': (31, 270),
         'text': f'&a{wins_until_wins} &fWins Until &6{target_wins}'},
        {'position': (31, 299),
         'text': f'&c{losses_until_losses} &fLosses Until &6{target_losses}'},
        {'position': (342, 212),
         'text': f'&a{final_kills_until_fkdr} &fFinal K Until &6{target_fkdr}'},
        {'position': (342, 241),
         'text': f'&a{final_kills_at_fkdr} &fFinal K At &6{target_fkdr}'},
        {'position': (342, 270),
         'text': f'&a{final_kills_until_final_kills} '
         f'&fFinal K Until &6{target_final_kills}'},
        {'position': (342, 299),
         'text': f'&c{final_deaths_until_final_deaths} '
         f'&fFinal D Until &6{target_final_deaths}'},
        {'position': (31, 343),
         'text': f'&a{beds_broken_until_bblr} &fBeds B Until &6{target_bblr}'},
        {'position': (31, 372),
         'text': f'&a{beds_broken_at_bblr} &fBeds B At &6{target_bblr}'},
        {'position': (31, 401),
         'text': f'&a{beds_broken_until_beds_broken} '
         f'&fBeds B Until &6{target_beds_broken}'},
        {'position': (31, 430),
         'text': f'&c{beds_lost_until_beds_lost} &fBeds L Until &6{target_beds_lost}'},
        {'position': (342, 343),
         'text': f'&a{kills_until_kdr} &fKills Until &6{target_kdr}'},
        {'position': (342, 372),
         'text': f'&a{kills_at_kdr} &fKills At &6{target_kdr}'},
        {'position': (342, 401),
         'text': f'&a{kills_until_kills} &fKills Until &6{target_kills}'},
        {'position': (342, 430),
         'text': f'&c{deaths_until_deaths} &fDeaths Until &6{target_deaths}'}
    ]

    for values in data:
        render_mc_text(
            image=image,
            shadow_offset=(2, 2),
            font=minecraft_16,
            **values
        )

    # Render stars until text
    formatted_lvl = get_formatted_level(stars_until_target)
    stars_until_txt = f'&7{stars_until_value} &fStars Until {formatted_lvl}'

    render_mc_text(
        text=stars_until_txt,
        position=(225, 169),
        font=minecraft_16,
        image=image,
        shadow_offset=(2, 2),
        align='center'
    )

    render_display_name(
        username=name,
        rank_info=rank_info,
        image=image,
        font_size=22,
        position=(225, 28),
        align='center'
    )

    render_progress_bar(
        level=level,
        progress_of_10=progress_of_10,
        position=(225, 89),
        image=image,
        align='center'
    )

    render_progress_text(
        progress=progress,
        target=target,
        position=(225, 120),
        image=image,
        align='center'
    )

    render_mc_text(
        text='Milestones',
        position=(536, 23),
        font=minecraft_18,
        image=image,
        shadow_offset=(2, 2),
        align='center'
    )

    render_mc_text(
        text=f'({mode.title()})',
        position=(536, 45),
        font=minecraft_16,
        image=image,
        shadow_offset=(2, 2),
        align='center'
    )

    paste_skin(skin_res, image, positions=(472, 61))

    image.save(f'./database/rendered/{save_dir}/{mode.lower()}.png')
