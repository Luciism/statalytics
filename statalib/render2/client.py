import os
from abc import ABC, abstractmethod
from io import BytesIO

from aiohttp import ClientSession, ClientTimeout

from statalib.render2.placeholders import PlaceholderValues


class RenderingClient(ABC):
    def __init__(self, route: str) -> None:
        self._route: str = route.removeprefix("/")

    async def render(self, background_image: bytes | None = None) -> bytes:
        formdata = self.placeholder_values().build_form_data(background_image)

        async with ClientSession(timeout=ClientTimeout(total=10)) as session:
            res = await session.post(
                f"{os.getenv('RENDERER_HOSTNAME')}/{self._route}", data=formdata
            )
            res.raise_for_status()

            render_bytes = await res.content.read()

        return render_bytes

    async def render_to_buffer(self, background_image: bytes | None = None) -> BytesIO:
        render = await self.render(background_image)

        img_bytes = BytesIO(render)
        _ = img_bytes.seek(0)

        return img_bytes

    @abstractmethod
    def placeholder_values(self) -> PlaceholderValues: ...
