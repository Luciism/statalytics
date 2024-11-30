"""Utility functions for image rendering."""

from io import BytesIO

import numpy as np
from PIL import Image


def image_to_bytes(image: Image.Image) -> bytes:
    """
    Convert a PIL `Image` object to bytes.

    :param image: The `Image` object to convert to bytes.
    :return bytes: The bytes representation of the image.
    """
    image_bytes = BytesIO()
    image.save(image_bytes, format='PNG')
    image_bytes.seek(0)

    return image_bytes


def recolor_pixels(
    image: Image.Image,
    rgb_from: tuple | list,
    rgb_to: tuple | list
) -> Image.Image:
    """
    Recolor all pixels of a certain RGB value to another in an image.

    :param image: The image to recolor pixels on.
    :param rgb_from: A list of RGB sets to recolor from.
    :param rgb_to: A list of RGB sets to recolor to.
    :return Image.Image: The recolored image.
    """
    data = np.array(image)  # "data" is a height x width x 4 numpy array
    red, green, blue, _ = data.T

    # Replace placeholder with other color... (leaves alpha values alone...)
    for rgb_from_val, rgb_to_val in zip(rgb_from, rgb_to):
        placeholders = (red == rgb_from_val[0]) & (green == rgb_from_val[1]) & (blue == rgb_from_val[2])
        data[..., :-1][placeholders.T] = rgb_to_val

    return Image.fromarray(data)
