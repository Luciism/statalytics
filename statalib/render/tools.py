from io import BytesIO

import numpy as np
from PIL import Image


def mc_text_shadow(rgb: tuple) -> tuple[int, int, int]:
    """
    Returns drop shadow RGB relative to passed RGB value
    :param rgb: The RGB value to get a shadow color for
    """
    return tuple([int(c * 0.25) for c in rgb])


def image_to_bytes(image: Image.Image) -> bytes:
    """
    Converts a PIL Image object to bytes
    :param image: the image object to convert to bytes
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
    Recolors all pixels of a certain RGB value to another in an image
    :param image: The image object to recolor
    :param rgb_from: a list of RGB sets to recolor from
    :param rgb_to: a list of RGB sets to recolor to
    """
    data = np.array(image)  # "data" is a height x width x 4 numpy array
    red, green, blue, _ = data.T

    # Replace placeholder with other color... (leaves alpha values alone...)
    for rgb_from_val, rgb_to_val in zip(rgb_from, rgb_to):
        placeholders = (red == rgb_from_val[0]) & (green == rgb_from_val[1]) & (blue == rgb_from_val[2])
        data[..., :-1][placeholders.T] = rgb_to_val

    return Image.fromarray(data)
