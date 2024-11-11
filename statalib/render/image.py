from io import BytesIO
from typing import Literal, TypedDict

from PIL import Image, UnidentifiedImageError

from . import text as imgtext
from .text import render_mc_text
from .prestige_colors import get_formatted_level
from ..assets import ASSET_LOADER
from ..calctools import RankInfo, PROGRESS_BAR_MAX


class TextOptions(TypedDict):
    """
    Typed dict for rendered text options.
    """
    font_size: int
    """The size of the font in pixels."""
    position: tuple[int, int]
    """The (x, y) position of the text on the image."""
    shadow_offset: tuple[int, int] | None
    """The (x, y) offset of the text shadow relative to the text."""
    align: Literal["left", "right", "center"]
    """Whether to align the text left, right, or center."""

    @staticmethod
    def default() -> 'TextOptions':
        return {
            "font_size": 16,
            "position": (0, 0),
            "shadow_offset": None,
            "align": "left"
        }


class PlayerRender:
    def __init__(self, image: Image.Image) -> None:
        self._image = image

    def render_hypixel_username(
        self,
        username: str,
        rank_info: RankInfo,
        text_options: TextOptions=TextOptions.default(),
        bedwars_level: int | None=None
    ) -> None:
        """
        Render the username of the player including rank, and optionally
        their bedwars level.

        :param username: The username of the player.
        :param rank_info: The rank info object for the player.
        :param text_options: The text configuration in which to use.
        :param bedwars_level: Optionally render the provided bedwars level of the player.
        """
        font = ASSET_LOADER.load_font("main.ttf", text_options.get("font_size", 16))

        full_string = f'{rank_info["formatted_prefix"]}{username}'

        if bedwars_level is not None:
            formatted_lvl = get_formatted_level(bedwars_level)
            full_string = f'{formatted_lvl} {full_string}'

        render_mc_text(
            text=full_string,
            position=text_options.get("position", (0, 0)),
            font=font,
            image=self._image,
            shadow_offset=text_options.get("shadow_offset", (2, 2)),
            align=text_options.get("align", "left")
        )

    def paste_skin(self, skin_model: bytes, position: tuple[int, int]) -> None:
        """
        Paste a skin model on to the image

        :param skin_model: The skin model image as bytes.
        :param position: The (X, Y) position to paste the skin.
        """
        try:
            skin = Image.open(BytesIO(skin_model))
        except UnidentifiedImageError:
            skin = ASSET_LOADER.load_image("steve_bust.png")

        composite_image = Image.new("RGBA", self._image.size)
        composite_image.paste(skin, position)
        self._image.alpha_composite(composite_image)


class TextRender:
    def __init__(self, image: Image.Image) -> None:
        self._image = image

    def draw(
        self,
        text: str,
        text_options: TextOptions=TextOptions.default()
    ) -> None:
        """
        Draws text using the specified text options.

        :param text: The text to draw.
        :param text_options: The text configuration in which to use.
        """
        if not "position" in text_options:
            text_options["position"] = (0, 0)
        render_mc_text(text, image=self._image, **text_options)

    def draw_many(
        self,
        text_info: list[tuple[str, TextOptions]],
        default_text_options: TextOptions
    ) -> None:
        """
        Draw many sets of text at once, all with the same text options.

        :param text_info: A list of texts to draw, including text options specific \
            to that text, for example:
            ```python
            [
                ("Hello, World!", {"font_size": 22})
            ]
            ```
        :param default_text_options: The default text options to apply when text options \
            are missing from the invidually specified texts.
        """
        for text, text_options in text_info:
            self.draw(text, {**default_text_options, **text_options})


class ProgressRender:
    font = ASSET_LOADER.load_font("main.ttf", 20)
    progress_symbol="|"

    def __init__(self, image: Image.Image, text_render: TextRender) -> None:
        self._image = image
        self._text_render = text_render

    def _actual_text_len(self, text: str) -> int:
        """Find the text length while ignoring color coding characters."""
        return imgtext.get_text_len(
            imgtext.get_actual_text(get_formatted_level(text)), font=self.font)

    def draw_progress_bar(
        self,
        level: int,
        progress_percentage: int | float,
        position: tuple[int, int],
        align: Literal["left", "right", "center"]="center"
    ) -> None:
        """
        Render a level progress bar.

        :param level: The current level to render the progress bar for.
        :param progress_percentage: The current progression percentage of the level.
        :param position: The (x, y) position of the progress bar.
        :param align: Whether to align the progress bar left, right, or center.
        """
        # Calculate how many characters to color
        xp_bar_progress = PROGRESS_BAR_MAX * progress_percentage / 100

        colored_chars = self.progress_symbol * int(xp_bar_progress)
        gray_chars = self.progress_symbol * (PROGRESS_BAR_MAX - int(xp_bar_progress))

        chars_text = f'&b{colored_chars}&7{gray_chars}'
        formatted_lvl_text = get_formatted_level(int(level))
        formatted_target_text = get_formatted_level(int(level)+1)

        self._text_render.draw(
            text=f'{formatted_lvl_text} {chars_text} {formatted_target_text}',
            text_options={
                "font_size": 20,
                "position": position,
                "shadow_offset": (2, 2),
                "align": align
            }
        )

    def draw_progress_text(
        self,
        progress: int,
        target: int,
        position: tuple[int, int],
        align: Literal['left', 'center', 'right'] = 'center'
    ) -> Image.Image:
        """
        Render progress text: `Progress: {progress} / {target}`
        :param progress: The xp progress made on the current level.
        :param target: The xp needed to reach the next level.
        :param position: The (x, y) position of the progress text.
        :param align: Whether to align the progress text left, right, or center.
        """
        self._text_render.draw(
            text=f'&fProgress: &d{progress:,} &f/ &a{target:,}',
            text_options={
                "font_size": 20,
                "position": position,
                "shadow_offset": (2, 2),
                "align": align
            }
        )


class ImageRender:
    def __init__(self, base_image: Image.Image):
        self._image: Image.Image = base_image.convert("RGBA")
        self.text = TextRender(self._image)
        self.player = PlayerRender(self._image)
        self.progress = ProgressRender(self._image, self.text)

    def overlay_image(self, overlay_image: Image.Image) -> None:
        """Composite / overlay another image onto the image."""
        self._image.alpha_composite(overlay_image.convert("RGBA"))

    def paste_titles(self, asset_dir: str) -> None:
        """
        Composite / overlay the respective titles image for the specified
        assets directory.

        :param assets_dir: The background assets dir that the titles are located \
            within.
        """
        titles_im = ASSET_LOADER.load_image(f"bg/{asset_dir}/title.png")
        self.overlay_image(titles_im)

    def to_bytes(self) -> bytes:
        """Return the image as bytes."""
        image_bytes = BytesIO()
        self._image.save(image_bytes, format='PNG')
        image_bytes.seek(0)

        return image_bytes

    def save(self, filepath: str, **kwargs) -> None:
        """Write the image to disk."""
        self._image.save(filepath, **kwargs)

    @property
    def size(self) -> tuple[int, int]:
        """The size of the image."""
        return self._image.size