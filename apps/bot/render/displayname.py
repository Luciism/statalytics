from statalib import HypixelData, render, hypixel, to_thread


@to_thread
def render_displayname(
    name: str,
    hypixel_data: HypixelData 
) -> bytes:
    hypixel_data = hypixel.get_player_dict(hypixel_data)

    level = hypixel_data.get('achievements', {}).get('bedwars_level', 0)
    rank_info = hypixel.get_rank_info(hypixel_data)

    image = render.usernames.render_display_name(
        username=name,
        rank_info=rank_info,
        level=level,
        image=None,
        font_size=35,
        position=(0, 0),
        shadow_offset=(4, 4),
        align='center'
    )

    return render.tools.image_to_bytes(image)
