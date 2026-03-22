import logging
import os
from abc import ABC, abstractmethod
from dataclasses import dataclass
from io import BytesIO
from typing import Hashable, Sequence

import cachetools.keys
from aiohttp import ClientSession, ClientTimeout
from cachetools import TTLCache
from cachetools_async import cached

from ..common import Mode
from .placeholders import PlaceholderValues, Size


logger = logging.getLogger(__name__)


@dataclass
class RenderingClientOptions:
    save_to_render_cache: bool = True
    render_id: str | None = None

def exclude_self_key(*args: Sequence[Hashable], **kwargs: frozenset[Hashable]):
    return cachetools.keys.hashkey(*args[1:], **kwargs)

class RenderingClient(ABC):
    def __init__(
        self, route: str, options: RenderingClientOptions | None = None
    ) -> None:
        self._route: str = route.removeprefix("/")

        self.mode: Mode | None = None
        self.options: RenderingClientOptions = options or RenderingClientOptions()

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
        if bypass_cache:
            return await self._make_request(self.placeholder_values(), background_image, size)

        return await self._make_request_with_cache(
            self.placeholder_values(), background_image, size
        )

    async def render_to_buffer(
        self, background_image: bytes | None = None, size: Size="regular", bypass_cache: bool = False
    ) -> BytesIO:
        render = await self.render(background_image, size, bypass_cache)

        img_bytes = BytesIO(render)
        _ = img_bytes.seek(0)

        return img_bytes

    @abstractmethod
    def placeholder_values(self) -> PlaceholderValues: ...
