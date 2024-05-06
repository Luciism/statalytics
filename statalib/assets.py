import json
import os

from PIL import Image, ImageFont

from .common import REL_PATH


class _AssetLoader:
    """Global lazy asset loader class."""

    def __init__(self) -> None:
        self.__command_map = None
        self.__loaded_images: dict[str, Image.Image] = {}
        self.__loaded_fonts: dict[tuple[str, int], ImageFont.FreeTypeFont] = {}
        self.__loaded_embeds: dict[str, dict] = {}


    @property
    def command_map(self) -> dict[str, str]:
        """Command id to command name mappings"""
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


    def load_image(self, image_path: str) -> Image.Image:
        """
        Load an image object by file path.
        :param image_path: The path to the image file relative to the assets directory.
        """
        if image_path not in self.__loaded_images:
            self.__loaded_images[image_path] = \
                Image.open(f"{REL_PATH}/assets/{image_path}")
        return self.__loaded_images[image_path]


    def load_font(self, font_file: str, font_size: int) -> ImageFont.FreeTypeFont:
        """
        Load a font object by file name.
        :param font_file: The name of the font file located in `assets/fonts/`.
        :param font_size: The font size to load the font in.
        """
        if (font_file, font_size) not in self.__loaded_fonts:
            self.__loaded_fonts[(font_file, font_size)] = \
                ImageFont.truetype(f"{REL_PATH}/assets/fonts/{font_file}", font_size)

        return self.__loaded_fonts[(font_file, font_size)]


    def load_embed(self, embed_file: str) -> dict:
        """
        Load an embed by file name.
        :param embed_file: The path to the embed file relative to `assets/embeds/`.
        """
        if embed_file not in self.__loaded_embeds:
            with open(f"{REL_PATH}/assets/embeds/{embed_file}") as df:
                self.__loaded_embeds[embed_file] = json.load(df)
        return self.__loaded_embeds[embed_file]


ASSET_LOADER = _AssetLoader()
