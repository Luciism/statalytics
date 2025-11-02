"""Functionality to lazy load assets into memory as needed."""

import functools
import json
import os
from dataclasses import dataclass

from PIL import Image, ImageFont

from .common import REL_PATH
from .errors import BackgroundPropertiesNotFoundError


class _AssetLoader:
    """Global lazy asset loader class."""

    def __init__(self) -> None:
        self.__command_map = None

    @property
    def command_map(self) -> dict[str, str]:
        """Command ID to command name mappings."""
        if self.__command_map is None:
            with open(f"{REL_PATH}/assets/command_map.json", encoding="utf-8") as file:
                self.__command_map = json.load(file)
        return self.__command_map

    def image_file_exists(self, image_path: str) -> bool:
        """
        Check whether an image file exists on the disk.

        :param image_path: The path to the image file relative to the assets directory.
        """
        return os.path.exists(f"{REL_PATH}/assets/{image_path}")

    @functools.lru_cache(maxsize=32)
    def __load_image(self, image_path: str) -> Image.Image:
        return Image.open(f"{REL_PATH}/assets/{image_path}")

    def load_image(self, image_path: str) -> Image.Image:
        """
        Load an image object by file path.

        :param image_path: The path to the image file relative to the assets directory.
        """
        return self.__load_image(image_path).copy()

    @functools.lru_cache(maxsize=32)
    def load_font(self, font_file: str, font_size: int) -> ImageFont.FreeTypeFont:
        """
        Load a font object by file name.

        :param font_file: The name of the font file located in `assets/fonts/`.
        :param font_size: The font size to load the font in.
        """
        return ImageFont.truetype(f"{REL_PATH}/assets/fonts/{font_file}", font_size)


ASSET_LOADER = _AssetLoader()
"Global asset loader instance."


@dataclass
class BackgroundProperties:
    """Properties for background image assets."""

    id: str
    "The ID of the background."
    name: str
    "The display name of the background assets."
    path: str
    "The assets path to the background assets (excludes trailing slashes)."
    size: tuple[int, int]
    "The (width, height) of the background image(s)."

    @staticmethod
    def get_by_id(background_id: str) -> "BackgroundProperties":
        """
        Load background properties from a background ID.

        :param background_id: The ID of the background to load properties for.
        :raises: BackgroundPropertiesNotFoundError: No properties were found for
            the specified background ID.
        """
        with open(f"{REL_PATH}/assets/bg/properties.json") as f:
            bgs: dict[str, list[dict[str, str | list[int]]]] = json.load(f)

        for bg in bgs["render_modes"]:
            if bg["id"] == background_id:
                return BackgroundProperties(
                    id=bg["id"],
                    name=bg["name"],
                    path=bg["path"].removesuffix("/").removesuffix("\\"),
                    size=(bg["size"][0], bg["size"][1]),
                )

        raise BackgroundPropertiesNotFoundError(
            f"Unknown background ID: {background_id}"
        )

    def full_path(self) -> str:
        """The full, absolute path to the background assets."""
        return f"{REL_PATH}/assets/bg/{self.path}"

    @staticmethod
    def get_all() -> list["BackgroundProperties"]:
        with open(f"{REL_PATH}/assets/bg/properties.json") as f:
            bgs: dict[str, list[dict[str, str | list[int]]]] = json.load(f)

        return [
            BackgroundProperties(
                id=bg["id"],
                name=bg["name"],
                path=bg["path"].removesuffix("/").removesuffix("\\"),
                size=(bg["size"][0], bg["size"][1]),
            )
            for bg in bgs["render_modes"]
        ]
