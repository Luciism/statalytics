from PIL import Image, ImageDraw, ImageFont

from calc.average import Ratios
from helper.rendername import get_rank_prefix, render_rank
from helper.rendertools import get_background, paste_skin, box_center_text
from helper.renderprogress import render_progress_bar, render_progress_text


def render_average(name, uuid, mode, hypixel_data, skin_res, save_dir):
    ratios = Ratios(name, mode, hypixel_data)
    level = ratios.level
    player_rank_info = ratios.player_rank_info
    progress, target, progress_out_of_10 = ratios.progress

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
        final_deaths_per_game,
        beds_lost_per_game,
        deaths_per_game,
    ) = ratios.get_per_game()


    clutch_rate = ratios.get_clutch_rate()
    loss_rate = ratios.get_loss_rate()

    most_wins = ratios.get_most_wins()
    most_losses = ratios.get_most_losses()

    green = (85, 255, 85)
    white = (255, 255, 255)
    red = (255, 76, 76)
    black = (0, 0, 0)

    image = get_background(path='./assets/average', uuid=uuid,
                           default='base', level=level, rank_info=player_rank_info)

    image = image.convert("RGBA")

    draw = ImageDraw.Draw(image)
    minecraft_16 = ImageFont.truetype('./assets/minecraft.ttf', 16)
    minecraft_18 = ImageFont.truetype('./assets/minecraft.ttf', 18)
    minecraft_22 = ImageFont.truetype('./assets/minecraft.ttf', 22)

    def leng(text, width):
        return (width - draw.textlength(text, font=minecraft_16)) / 2

    data = (
        ((leng(wins_per_star, 141)+18, 249), wins_per_star, green),
        ((leng(final_kills_per_star, 141)+18, 309), final_kills_per_star, green),
        ((leng(beds_broken_per_star, 141)+18, 369), beds_broken_per_star, green),
        ((leng(kills_per_star, 141)+18, 429), kills_per_star, green),

        ((leng(losses_per_star, 141)+172, 249), losses_per_star, red),
        ((leng(final_deaths_per_star, 141)+172, 309), final_deaths_per_star, red),
        ((leng(beds_lost_per_star, 141)+172, 369), beds_lost_per_star, red),
        ((leng(deaths_per_star, 141)+172, 429), deaths_per_star, red),

        ((leng(clutch_rate, 141)+326, 249), clutch_rate, green),
        ((leng(final_kills_per_game, 141)+326, 309), final_kills_per_game, green),
        ((leng(beds_broken_per_game, 141)+326, 369), beds_broken_per_game, green),
        ((leng(kills_per_game, 141)+326, 429), kills_per_game, green),

        ((leng(loss_rate, 142)+480, 249), loss_rate, red),
        ((leng(final_deaths_per_game, 142)+480, 309), final_deaths_per_game, red),
        ((leng(beds_lost_per_game, 142)+480, 369), beds_lost_per_game, red),
        ((leng(deaths_per_game, 142)+480, 429), deaths_per_game, red),

        ((leng(most_wins, 201)+18, 189), most_wins, green),
        ((leng(most_losses, 201)+232, 189), most_losses, red),
        ((leng(f'({mode.title()})', 171)+451, 46), f'({mode.title()})', white)
    )

    for values in data:
        start_x, start_y = values[0]
        stat = values[1]

        draw.text((start_x + 2, start_y + 2), stat, fill=black, font=minecraft_16)
        draw.text((start_x, start_y), stat, fill=values[2], font=minecraft_16)

    # Render name & progress bar
    rank_prefix = get_rank_prefix(player_rank_info)
    totallength = draw.textlength(f'{rank_prefix}{name}', font=minecraft_22)
    player_x = round((415 - totallength) / 2) + 18

    render_rank(name, position_x=player_x, position_y=26, rank_prefix=rank_prefix,
                player_rank_info=player_rank_info, draw=draw, fontsize=22)

    render_progress_bar(box_positions=(415, 18), position_y=88, level=level,
                        progress_out_of_10=progress_out_of_10, image=image)

    render_progress_text(box_positions=(415, 18), position_y=119,
                         progress=progress, target=target, draw=draw)

    # Paste overlay
    overlay_image = Image.open(f'./assets/average/overlay.png')
    overlay_image = overlay_image.convert("RGBA")
    image.paste(overlay_image, (0, 0), overlay_image)

    box_center_text("Average Stats", draw, box_width=171,
                    box_start=451, text_y=25, font=minecraft_18)

    # Render skin
    image = paste_skin(skin_res, image, positions=(465, 67))

    # Save the image
    image.save(f'./database/activerenders/{save_dir}/{mode.lower()}.png')
