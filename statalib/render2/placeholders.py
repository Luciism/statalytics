"""Placeholder values for rendering."""

import json
import typing
from base64 import b64encode
from collections.abc import Mapping
from dataclasses import dataclass
from datetime import datetime, UTC
from typing_extensions import override

import aiohttp

from ..hypixel.leveling import LevelProgressionTuple
from ..hypixel.ranks import PlayerRank
from ..fmt import ordinal
from ..color import Color
from ..render import Prestige


Size = typing.Literal["small", "regular", "large"]

@dataclass(unsafe_hash=True)
class TSpan:
    """Rich text span."""
    value: str
    """The text of the span."""
    fill: str | None = None
    """The color of the span."""
    font_size: int | str | None = None
    """The font size of the span."""
    font_weight: int | None = None
    """The font weight of the span."""
    font_family: str | None = None
    """The font family of the span."""

    def as_dict(self) -> dict[str, typing.Any]:
        return self.__dict__


@dataclass
class PlaceholderValues:
    images: dict[str, str]
    """The image related placeholder values."""
    shapes: dict[str, str]
    """The shape related placeholder values."""
    text: dict[str, str | TSpan | list[TSpan]]
    """The text related placeholder values."""

    @staticmethod
    def new(
        text: Mapping[str, str | TSpan | list[TSpan]] | None=None,
        images: dict[str, str] | None=None,
        shapes: dict[str, str] | None=None,
    ) -> "PlaceholderValues":
        """
        Create a new placeholder values object.

        :param text: The text related placeholder values.
        :param images: The image related placeholder values.
        :param shapes: The shape related placeholder values.
        """
        return PlaceholderValues(
            text=dict(text or {}),
            shapes=shapes or {},
            images=images or {},
        )

    def as_dict(self) -> dict[str, typing.Any]:
        text = {}

        for k, v in self.text.items():
            if type(v) == str:
                text[k] = v
            elif type(v) == list:
                text[k] = [t.as_dict() for t in v]
            elif type(v) == TSpan:
                text[k] = v.as_dict()

        return {
            "images": self.images,
            "shapes": self.shapes,
            "text": text
        }

    def add_progress_bar(
        self,
        colors: tuple[Color, Color, Color, Color, Color, Color, Color],
        progress_percent: float,
    ) -> None:
        """
        Add standard progress bar placeholder values.

        :param colors: The seven step color gradient.
        :param progress_percent: The progress percentage (how much of the bar is filled).
        """
        progress_percent = max(min(progress_percent, 100), 0)

        for i, color in enumerate(colors):
            self.shapes[f"progress_bar#gradientStop.{i}"] = color.hex

        self.shapes[f"progress_bar#width"] = f"{progress_percent}%"

    def add_skin_model(
        self, skin_model_img: bytes, placeholder_key: str="skin_model"
    ) -> None:
        """
        Add skin model placeholder values, converting the image to base64.

        :param skin_model_img: The skin model image.
        :param placeholder_key: The placeholder key to use.
        """
        skin_base64 = b64encode(skin_model_img).decode("utf-8")
        self.images[f"{placeholder_key}#href"] = f"data:image/png;base64,{skin_base64}"

    def add_footer_text(self) -> None:
        """Add the standard footer text placeholder value."""
        now = datetime.now(UTC)
        self.text["footer_info#text"] = [
            TSpan(value="statalytics.net • ", fill="#FFFFFF"),
            TSpan(value=now.strftime(f"%A %d{ordinal(now.day)} %B, %Y"), fill="#ABABAB", font_weight=300),
        ]
        

    def add_current_level(self, current_level: int, placeholder_key: str="level_current") -> None:
        """
        Add the current level text placeholder value colored appropriately as tspans.

        :param current_level: The current level.
        :param placeholder_key: The placeholder key to use.
        """
        prestige = Prestige(current_level)

        self.text[f"{placeholder_key}#text"] = [
            TSpan(value=char, fill=color.hex)
            for char, color in prestige.char_to_color_map()
        ]

    def add_next_level(self, next_level: int, placeholder_key: str="level_next") -> None:
        """
        Add the next level text placeholder value colored appropriately as tspans.

        :param next_level: The next level.
        :param placeholder_key: The placeholder key to use.
        """
        prestige = Prestige(next_level)

        self.text[f"{placeholder_key}#text"] = [
            TSpan(value=char, fill=color.hex)
            for char, color in prestige.char_to_color_map()
        ]

    def add_current_and_next_level(self, current_level: int) -> None:
        """Add both current and next level text placeholder values."""
        self.add_current_level(current_level)
        self.add_next_level(current_level + 1)

    def add_xp_progress_text(self, xp_progress: LevelProgressionTuple) -> None:
        """
        Add the xp progress text placeholder value.

        :param xp_progress: The xp progress tuple.
        """
        self.text["xp_progress#text"] = [TSpan(f"{xp_progress.progress:,} / {xp_progress.target:,} xp")]

    def add_playername(self, rank: PlayerRank, placeholder_key: str="displayname") -> None:
        """
        Add the playername text placeholder value appropriately color with the player's
        rank information.

        :param rank: The player rank, contains the username.
        :param placeholder_key: The placeholder key to use.
        """
        # Reduce the font size if the username is too long
        length = len(f"{rank.prefix}{rank.username}")
        max_len = 18

        if length > max_len:
            font_size = max(1 - (length - max_len) * 0.035, 0.1)
        else:
            font_size = 1

        self.text[f"{placeholder_key}#text"] = [
            TSpan(value=part[0], fill=part[1].hex, font_size=f"{font_size}em") for part in rank.parts_with_username
        ]


    def build_form_data(
        self, background_image: bytes | None, size: Size="regular"
    ) -> aiohttp.FormData:
        """
        Build the form data for the request.

        :param background_image: The background image to use.
        :param size: The size of the image to render.
        """
        data = aiohttp.FormData()
        data.add_field("scale", size, filename="blob", content_type="application/json")
        data.add_field(
            "placeholder_values",
            json.dumps(self.as_dict()).encode("utf-8"),
            filename="blob",
            content_type="application/json",
        )

        if background_image is not None:
            data.add_field(
                "background_image",
                background_image,
                filename="blob",
                content_type="image/png",
            )

        return data


    @override
    def __hash__(self) -> int:
        hashable_text: list[tuple[str, typing.Any]] = []

        for k, v in self.text.items():
            if isinstance(v, list):
                hashable_text.append((k, tuple(v)))
            else:
                hashable_text.append((k, v))

        return hash((
            frozenset(self.images.items()),
            frozenset(self.shapes.items()),
            frozenset(hashable_text),
        ))

