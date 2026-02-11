import json
import typing
from base64 import b64encode
from dataclasses import dataclass
from datetime import datetime, UTC

import aiohttp

from ..hypixel.leveling import LevelProgressionTuple
from ..hypixel.ranks import PlayerRank
from ..fmt import ordinal
from ..color import Color
from ..render import Prestige


@dataclass
class TSpan:
    value: str
    fill: str | None = None
    font_size: int | None = None
    font_weight: int | None = None
    font_family: str | None = None

    def as_dict(self) -> dict[str, typing.Any]:
        return self.__dict__


@dataclass
class PlaceholderValues:
    images: dict[str, str]
    shapes: dict[str, str]
    text: dict[str, list[TSpan]]

    @staticmethod
    def new(
        text: dict[str, list[TSpan]] | None=None,
        images: dict[str, str] | None=None,
        shapes: dict[str, str] | None=None,
    ) -> "PlaceholderValues":
        return PlaceholderValues(
            text=text or {},
            shapes=shapes or {},
            images=images or {},
        )

    def as_dict(self) -> dict[str, typing.Any]:
        return {
            "images": self.images,
            "shapes": self.shapes,
            "text": {k: [t.as_dict() for t in v] for k, v in self.text.items()}
        }

    def add_progress_bar(
        self,
        colors: tuple[Color, Color, Color, Color, Color, Color, Color],
        progress_percent: float,
    ) -> None:
        progress_percent = max(min(progress_percent, 100), 0)

        for i, color in enumerate(colors):
            self.shapes[f"progress_bar#gradientStop.{i}"] = color.hex

        self.shapes[f"progress_bar#width"] = f"{progress_percent}%"

    def add_skin_model(
        self, skin_model_img: bytes
    ) -> None:
        skin_base64 = b64encode(skin_model_img).decode("utf-8")
        self.images["skin_model#href"] = f"data:image/png;base64,{skin_base64}"

    def add_footer_text(
        self
    ) -> None:
        now = datetime.now(UTC)
        self.text["footer_info#text"] = [
            TSpan(value="statalytics.net • ", fill="#FFFFFF"),
            TSpan(value=now.strftime(f"%A %d{ordinal(now.day)} %B, %Y"), fill="#ABABAB", font_weight=300),
        ]


    def add_current_and_next_level(self, current_level: int) -> None:
        prestige = Prestige(current_level)
        prestige_next = Prestige(current_level + 1)

        self.text["level_current#text"] = [
            TSpan(value=char, fill=color.hex)
            for char, color in prestige.char_to_color_map()
        ]
        self.text["level_next#text"] = [
            TSpan(value=char, fill=color.hex)
            for char, color in prestige_next.char_to_color_map()
        ]

    def add_xp_progress_text(self, xp_progress: LevelProgressionTuple) -> None:
        self.text["xp_progress#text"] = [TSpan(f"{xp_progress.progress:,} / {xp_progress.target:,} xp")]

    def add_playername(self, rank: PlayerRank) -> None:
        self.text["displayname#text"] = [
            TSpan(value=part[0], fill=part[1].hex) for part in rank.parts_with_username
        ]


    def build_form_data(
        self, background_image: bytes | None
    ) -> aiohttp.FormData:
        data = aiohttp.FormData()
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

