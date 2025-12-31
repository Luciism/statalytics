from PIL import Image, ImageDraw
from statalib import to_thread
from statalib.hypixel.lbs import LeaderboardData, LeaderboardPlayerEntry
from statalib.render import ImageRender
from statalib.render.image import TextOptions

WIDTH = 850
ROW_HEIGHT = 50
GAP = 6
FONT_SIZE = 26

BG_RADIUS = 8
BG_OPACITY = 50

DEFAULT_TEXT_OPTS: TextOptions = {
    "shadow_offset": (2, 2),
    "align": "left",
    "font_size": FONT_SIZE,
}


def calc_text_y(top: int) -> int:
    return round((top + (ROW_HEIGHT / 2)) - FONT_SIZE / 2)


def draw_rounded_rect(
    box: tuple[int, int, int, int], draw: ImageDraw.ImageDraw
) -> None:
    draw.rounded_rectangle(box, radius=BG_RADIUS, fill=(0, 0, 0, BG_OPACITY))


def draw_player_entry(
    im: ImageRender,
    draw: ImageDraw.ImageDraw,
    player: LeaderboardPlayerEntry,
    lb_position: int,
    top: int,
) -> None:
    bottom = top + ROW_HEIGHT
    text_y = calc_text_y(top)

    draw_rounded_rect((0, top, WIDTH, bottom), draw)

    im.text.draw(
        f"#{lb_position}",
        {**DEFAULT_TEXT_OPTS, "position": (90, text_y), "align": "right"},
    )
    im.text.draw(
        f'{player.rank_info["formatted_prefix"]}{player.username}',
        {**DEFAULT_TEXT_OPTS, "position": (120, text_y)},
    )
    im.text.draw(
        player.value, {**DEFAULT_TEXT_OPTS, "position": (650, text_y), "align": "left"}
    )


def draw_header(
    leaderboard: LeaderboardData, im: ImageRender, draw: ImageDraw.ImageDraw
) -> None:
    header_y = calc_text_y(0)
    draw_rounded_rect((0, 0, WIDTH, ROW_HEIGHT), draw)

    im.text.draw(
        "Pos",
        {**DEFAULT_TEXT_OPTS, "position": (90, header_y), "align": "right"},
    )

    im.text.draw("Player", {**DEFAULT_TEXT_OPTS, "position": (120, header_y)})

    im.text.draw(
        f"{leaderboard.info.title}",
        {**DEFAULT_TEXT_OPTS, "position": (650, header_y), "align": "left"},
    )


@to_thread
def render_leaderboard_chunk(
    leaderboard: LeaderboardData,
    players: list[LeaderboardPlayerEntry],
    starting_pos: int,
    include_header: bool = False,
) -> bytes:
    column_amount = len(players) + int(include_header)

    im = ImageRender(
        Image.new(
            "RGBA",
            (WIDTH, ROW_HEIGHT * column_amount + GAP * (column_amount - 1)),
            (0, 0, 0, 0),
        )
    )
    draw = ImageDraw.Draw(im._image)

    if include_header:
        draw_header(leaderboard, im, draw)

    for i, player in enumerate(players):
        y = (i + int(include_header)) * (ROW_HEIGHT + GAP)
        lb_position = starting_pos + i

        draw_player_entry(im, draw, player, lb_position, y)

    return im.to_bytes()
