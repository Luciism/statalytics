"""Functionality to lazy load assets into memory as needed."""

import json
import os
import functools

from PIL import Image, ImageFont

from .common import REL_PATH


class _AssetLoader:
    """Global lazy asset loader class."""

    def __init__(self) -> None:
        self.__command_map = None

    @property
    def command_map(self) -> dict[str, str]:
        """Command ID to command name mappings."""
        if self.__command_map is None:
            with open(f"{REL_PATH}/assets/command_map.json") as df:
                self.__command_map = json.load(df)
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
