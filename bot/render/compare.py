from PIL import Image, ImageDraw, ImageFont

from calc.compare import Compare
from helper.rendername import render_level_and_name
from helper.rendertools import get_background

def render_compare(name_1, name_2, uuid_1, mode,
                   hypixel_data_1, hypixel_data_2, save_dir):
    compare = Compare(name_1, name_2, mode, hypixel_data_1, hypixel_data_2)
    level_1, level_2 = compare.level_1, compare.level_2
    rank_info_1, rank_info_2 = compare.player_rank_info

    wins, losses, wlr, wins_diff, losses_diff, wlr_diff = compare.get_wins()
    final_kills, final_deaths, fkdr, final_kills_diff, final_deaths_diff, fkdr_diff = compare.get_finals()
    beds_broken, beds_lost, bblr, beds_broken_diff, beds_lost_diff, bblr_diff = compare.get_beds()
    kills, deaths, kdr, kills_diff, deaths_diff, kdr_diff = compare.get_kills()

    image = get_background(path='./assets/compare', uuid=uuid_1,
                           default='base', level=level_1, rank_info=rank_info_1)

    image = image.convert("RGBA")

    draw = ImageDraw.Draw(image)
    minecraft_16 = ImageFont.truetype('./assets/minecraft.ttf', 16)

    def leng(text, container_width):
        """Returns startpoint for centering text in a box"""
        return (container_width - draw.textlength(text, font=minecraft_16)) / 2

    green = (85, 255, 85)
    red = (255, 85, 85)
    white = (255, 255, 255)
    black = (0, 0, 0)
    gold = (255, 170, 0)

    def color(value, method):
        if method == 'g': color = green if value[0] == '+' else red
        elif method == 'b': color = red if value[0] == '+' else green
        return color

    data = (
        ((leng(wins, 195)+17, 110), wins, green),
        ((leng(wins_diff, 195)+17, 144), wins_diff, color(wins_diff, 'g')),

        ((leng(losses, 195)+223, 110), losses, red),
        ((leng(losses_diff, 195)+223, 144), losses_diff, color(losses_diff, 'b')),

        ((leng(wlr, 195)+429, 110), wlr, gold),
        ((leng(wlr_diff, 195)+429, 144), wlr_diff, color(wlr_diff, 'g')),

        ((leng(final_kills, 195)+17, 208), final_kills, green),
        ((leng(final_kills_diff, 195)+17, 242), final_kills_diff, color(final_kills_diff, 'g')),

        ((leng(final_deaths, 195)+223, 208), final_deaths, red),
        ((leng(final_deaths_diff, 195)+223, 242), final_deaths_diff, color(final_deaths_diff, 'b')),

        ((leng(fkdr, 195)+429, 208), fkdr, gold),
        ((leng(fkdr_diff, 195)+429, 242), fkdr_diff, color(fkdr_diff, 'g')),

        ((leng(beds_broken, 195)+17, 306), beds_broken, green),
        ((leng(beds_broken_diff, 195)+17, 340), beds_broken_diff, color(beds_broken_diff, 'g')),

        ((leng(beds_lost, 195)+223, 306), beds_lost, red),
        ((leng(beds_lost_diff, 195)+223, 340), beds_lost_diff, color(beds_lost_diff, 'b')),

        ((leng(bblr, 195)+429, 306), bblr, gold),
        ((leng(bblr_diff, 195)+429, 340), bblr_diff, color(bblr_diff, 'g')),

        ((leng(kills, 195)+17, 404), kills, green),
        ((leng(kills_diff, 195)+17, 438), kills_diff, color(kills_diff, 'g')),

        ((leng(deaths, 195)+223, 404), deaths, red),
        ((leng(deaths_diff, 195)+223, 438), deaths_diff, color(deaths_diff, 'b')),

        ((leng(kdr, 195)+429, 404), kdr, gold),
        ((leng(kdr_diff, 195)+429, 438), kdr_diff, color(kdr_diff, 'g')),

        ((leng(f'({mode})', 195)+429, 47), f'({mode})', white)
    )

    for values in data:
        start_x, start_y = values[0]
        stat = values[1]

        draw.text((start_x + 2, start_y + 2), stat, fill=black, font=minecraft_16)
        draw.text((start_x, start_y), stat, fill=values[2], font=minecraft_16)

    # Render Name
    render_level_and_name(name_1, level_1, rank_info_1, image=image,
                          box_positions=(17, 401), position_y=14, fontsize=18)

    render_level_and_name(name_2, level_2, rank_info_2, image=image,
                          box_positions=(17, 401), position_y=51, fontsize=18)

    # Paste overlay
    overlay_image = Image.open(f'./assets/compare/overlay.png')
    overlay_image = overlay_image.convert("RGBA")
    image.paste(overlay_image, (0, 0), overlay_image)

    # Save the image
    image.save(f'./database/activerenders/{save_dir}/{mode.lower()}.png')
