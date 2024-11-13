from statalib import render, get_rank_info, to_thread, get_player_dict


@to_thread
def render_displayname(
    name: str,
    hypixel_data: dict
) -> bytes:
    hypixel_data = get_player_dict(hypixel_data)

    level = hypixel_data.get('achievements', {}).get('bedwars_level', 0)
    rank_info = get_rank_info(hypixel_data)

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
