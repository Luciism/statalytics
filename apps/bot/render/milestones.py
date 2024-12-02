from calc.milestones import MilestonesStats
from statalib import sessions, to_thread, REL_PATH
from statalib.render import ImageRender, BackgroundImageLoader, Prestige


bg = BackgroundImageLoader(dir="milestones")

@to_thread
def render_milestones(
    name: str,
    uuid: str,
    mode: str,
    session_info: sessions.BedwarsSession,
    hypixel_data: dict,
    skin_model: bytes,
    save_dir: str
) -> None:
    stats = MilestonesStats(session_info, hypixel_data, mode)

    stars_until_value, stars_until_target = stats.get_stars()

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

    im = ImageRender(bg.load_background_image(uuid, {
        "level": stats.level, "rank_info": stats.rank_info}))

    # Render the stat values
    im.text.draw_many([
        (f'&a{wins_until_wlr} &fWins Until &6{target_wlr}', {'position': (31, 212)}),
        (f'&a{wins_at_wlr} &fWins At &6{target_wlr}', {'position': (31, 241)}),
        (f'&a{wins_until_wins} &fWins Until &6{target_wins}', {'position': (31, 270)}),
        (f'&c{losses_until_losses} &fLosses Until &6{target_losses}',
         {'position': (31, 299)}),
        (f'&a{final_kills_until_fkdr} &fFinal K Until &6{target_fkdr}',
         {'position': (342, 212)}),
        (f'&a{final_kills_at_fkdr} &fFinal K At &6{target_fkdr}',
         {'position': (342, 241)}),
        (f'&a{final_kills_until_final_kills} &fFinal K Until &6{target_final_kills}',
         {'position': (342, 270)}),
        (f'&c{final_deaths_until_final_deaths} '
         f'&fFinal D Until &6{target_final_deaths}',
         {'position': (342, 299)}),
        (f'&a{beds_broken_until_bblr} &fBeds B Until &6{target_bblr}',
         {'position': (31, 343)}),
        (f'&a{beds_broken_at_bblr} &fBeds B At &6{target_bblr}',
         {'position': (31, 372)}),
        (f'&a{beds_broken_until_beds_broken} &fBeds B Until &6{target_beds_broken}',
         {'position': (31, 401)}),
        (f'&c{beds_lost_until_beds_lost} &fBeds L Until &6{target_beds_lost}',
         {'position': (31, 430)}),
        (f'&a{kills_until_kdr} &fKills Until &6{target_kdr}',
         {'position': (342, 343)}),
        (f'&a{kills_at_kdr} &fKills At &6{target_kdr}', {'position': (342, 372)}),
        (f'&a{kills_until_kills} &fKills Until &6{target_kills}',
         {'position': (342, 401)}),
        (f'&c{deaths_until_deaths} &fDeaths Until &6{target_deaths}',
         {'position': (342, 430)}),
    ], default_text_options={
        "shadow_offset": (2, 2), "align": "left", "font_size": 16
    })

    # Render stars until text
    formatted_lvl = Prestige(stars_until_target).formatted_level
    stars_until_txt = f'&7{stars_until_value} &fStars Until {formatted_lvl}'

    im.text.draw(stars_until_txt, {
        "position": (225, 169),
        "font_size": 16,
        "shadow_offset": (2, 2),
        "align": "center"
    })

    lvl_progress, lvl_target, lvl_progress_percent = stats.leveling.progression

    im.player.render_hypixel_username(
        name, stats.rank_info, text_options={
        "align": "center",
        "font_size": 22,
        "position": (225, 28)
    })

    im.progress.draw_progress_bar(
        stats.level,
        progress_percentage=lvl_progress_percent,
        position=(225, 89),
        align="center"
    )
    im.progress.draw_progress_text(
        lvl_progress, lvl_target, position=(225, 120), align="center")

    im.text.draw("Milestones", text_options={
        "position": (536, 23),
        "font_size": 18,
        "shadow_offset": (2, 2),
        "align": "center"
    })

    im.text.draw(f'({stats.title_mode})', text_options={
        "position": (536, 45),
        "font_size": 16,
        "shadow_offset": (2, 2),
        "align": "center"
    })

    im.player.paste_skin(skin_model, position=(472, 61))

    im.save(f'{REL_PATH}/database/rendered/{save_dir}/{mode.lower()}.png')
