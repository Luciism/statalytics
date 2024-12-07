"""A handful of useful loose functions."""

import json
import typing
import asyncio
import functools
from typing import Literal
from datetime import datetime, UTC

import discord

from .cfg import config
from .common import REL_PATH


def get_embed_color(embed_type: Literal["primary", "warning", "danger"]) -> int:
    """
    Get a base 16 integer for a specfied embed color.

    :param embed_type: The embed color type (primary, warning, or danger).
    """
    return int(config(f'apps.bot.embeds.{embed_type}_color'), base=16)


def _set_embed_color(embed: discord.Embed, color: str | int):
    if color is not None:
        embed.color = color if isinstance(color, int) else get_embed_color(color)
    return embed


def __format_embed_fields(
    embed_json: dict,
    prop_values: dict[int, dict[str, dict[str, str]]]
) -> None:
    # loop over each field to format
    for field_index, field in prop_values.items():
        # get the embed field currently being targeted
        target_field: dict[str, str] = embed_json['fields'][field_index]

        for field_prop_name, field_prop_values in field.items():
            # format the property of the target field
            target_field[field_prop_name] = \
                target_field[field_prop_name].format(**field_prop_values)


def load_embeds(
    filename: str,
    format_values: dict[str, dict[str, str] | list[dict[str, dict[str, str]]]]=None,
    color: int | Literal['primary', 'warning', 'danger']=None
) -> list[discord.Embed]:
    """
    Loads a list of embeds from a json file.

    Example:
    ```python
    load_embeds(
        filename='example',
        format_values={
            'title': {
                'some_format_key': 'some_format_value'
            },
            'description': {
                'example': 'value',
                'hello': 'world'
            },
            'fields': {
                0: {
                    'name': {
                        'foo': 'bar'
                    }
                }
                2: {
                    'value': {
                        'foo': 'bar'
                    }
                }
            }
        }
    )
    ```
    :param filename: The name of the file containing the embed json data\
        (.json ext optional).
    :param format_values: A list of format values respective to their properties.
    :param color: Override embed color, can be integer directly or 'primary',\
        'warning', 'danger'.
    """
    if not filename.endswith('.json'):
        filename += '.json'

    # Load embed data
    with open(f"{REL_PATH}/assets/embeds/{filename}") as df:
        embed_dict = json.load(df)

    embeds = []

    # loop over actual embeds
    for embed_json in embed_dict['embeds']:
        if format_values is not None:
            # the property to format (eg: description)
            for prop_name, prop_values in format_values.items():
                # if the property is a list of fields,
                # format every field to use the format values
                if prop_name == 'fields':
                    __format_embed_fields(embed_json, prop_values)
                else:
                    embed_json[prop_name] = embed_json[prop_name].format(**prop_values)

        # load Embed item from embed json dict and set color
        embed = discord.Embed.from_dict(embed_json)
        embeds.append(_set_embed_color(embed, color))

    return embeds


def to_thread(func: typing.Callable) -> typing.Coroutine:
    """Converts a function to run on a separate thread."""
    @functools.wraps(func)
    async def wrapper(*args, **kwargs):
        return await asyncio.to_thread(func, *args, **kwargs)
    return wrapper


# I don't have a fucking clue mate.
def timezone_relative_timestamp(timestamp: int | float):
    """
    Adds local time difference to a UTC timestamp.

    :param timestamp: The timestamp to modify.
    """
    now_timestamp = datetime.now().timestamp()
    utcnow_timestamp = datetime.now(UTC).timestamp()

    timezone_difference = now_timestamp - utcnow_timestamp

    return timestamp + timezone_difference
