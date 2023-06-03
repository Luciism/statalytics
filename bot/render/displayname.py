from io import BytesIO
from PIL import Image, ImageFont, ImageDraw
from helper.calctools import get_player_rank_info
from helper.rendername import get_rank_prefix, render_level_and_name

def render_displayname(name, hypixel_data):
    level = hypixel_data.get('player', {}).get('achievements', {}).get('bedwars_level', 0)
    player_rank_info = get_player_rank_info(hypixel_data=hypixel_data.get('player', {}))
    rank_prefix = get_rank_prefix(player_rank_info)
    
    # Open the base image
    sample_image = Image.new('RGBA', (0, 0), (0, 0, 0, 0))
    draw = ImageDraw.Draw(sample_image)
    font = ImageFont.truetype('./assets/minecraft.ttf', 20)

    image_width = int(draw.textlength(f'[{level}] {rank_prefix} {name}', font=font)) + 18
    actual_image = Image.new('RGBA', (image_width, 20), (0, 0, 0, 0))

    render_level_and_name(name, level, player_rank_info, image=actual_image,
                          box_positions=(0, image_width-6), position_y=0, fontsize=20)

    # Return the result
    image_bytes = BytesIO()
    actual_image.save(image_bytes, format='PNG')
    image_bytes.seek(0)

    return image_bytes
