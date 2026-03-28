"""A client for interacting with the rendering service."""

import logging
import os
from abc import ABC, abstractmethod
from io import BytesIO
from typing import Hashable, Sequence

import cachetools.keys
from aiohttp import ClientSession, ClientTimeout
from cachetools import TTLCache
from cachetools_async import cached

from ..common import Mode
from .placeholders import PlaceholderValues, Size
from .backgrounds import load_background_for_user


logger = logging.getLogger(__name__)



def exclude_self_key(*args: Sequence[Hashable], **kwargs: frozenset[Hashable]):
    return cachetools.keys.hashkey(*args[1:], **kwargs)

class RenderingClient(ABC):
    """Rendering base client."""
    def __init__(self, route: str) -> None:
        """
        :param route: The rendering server route to send requests to.
        """
        self._route: str = route.removeprefix("/")

        self.mode: Mode | None = None


    @staticmethod
    def bg(
        discord_user_id: int,
        render_name: str,
        player_uuid: str | None=None,
    ) -> bytes | None:
        """
        Wrapper for `render2.backgrounds.load_background_for_user`.

        :param discord_user_id: The Discord ID of the user.
        :param render_name: The name of the render to load the background for.
        :param player_uuid: The UUID of the player to override the Discord ID for.
        """
        return load_background_for_user(discord_user_id, render_name, player_uuid)


    async def _make_request(
        self, placeholder_values: PlaceholderValues, background_image: bytes | None, size: Size
    ) -> bytes:
        formdata = placeholder_values.build_form_data(background_image, size)

        async with ClientSession(timeout=ClientTimeout(total=10)) as session:
            res = await session.post(
                f"{os.getenv('RENDERER_HOSTNAME')}/{self._route}", data=formdata
            )
            res.raise_for_status()

            render_bytes = await res.content.read()

        return render_bytes


    @cached(cache=TTLCache(ttl=600, maxsize=20), key=exclude_self_key)
    async def _make_request_with_cache(
        self, placeholder_values: PlaceholderValues, background_image: bytes | None, size: Size
    ) -> bytes:
        logger.debug("LRU renderer cache miss.")
        return await self._make_request(placeholder_values, background_image, size)

    async def render(
        self,
        background_image: bytes | None = None,
        size: Size="regular",
        bypass_cache: bool = False
    ) -> bytes:
        """
        Render the placeholder values.

        :param background_image: The background image to use.
        :param size: The size of the image to render.
        :param bypass_cache: Bypass the cache and make a new request.
        """
        if bypass_cache:
            return await self._make_request(self.placeholder_values(), background_image, size)

        return await self._make_request_with_cache(
            self.placeholder_values(), background_image, size
        )

    async def render_to_buffer(
        self, background_image: bytes | None = None, size: Size="regular", bypass_cache: bool = False
    ) -> BytesIO:
        """
        Render the placeholder values to a buffer.

        :param background_image: The background image to use.
        :param size: The size of the image to render.
        :param bypass_cache: Bypass the cache and make a new request.
        """
        render = await self.render(background_image, size, bypass_cache)

        img_bytes = BytesIO(render)
        _ = img_bytes.seek(0)

        return img_bytes

    @abstractmethod
    def placeholder_values(self) -> PlaceholderValues:
        """Abstract method to return the placeholder values."""
        ...
