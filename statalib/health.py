from typing import Callable, final

from aiohttp import web

@final
class HealthMicroApp(web.Application):
    def __init__(
        self,
        is_ready_callable: Callable[[], bool],
    ) -> None:
        super().__init__()

        self.is_ready = is_ready_callable

        _ = self.router.add_get("/live", self.live)
        _ = self.router.add_get("/ready", self.ready)

        self.runner: web.AppRunner | None = None
        self.site: web.TCPSite | None = None
    
    async def live(self, _: web.Request):
        return web.Response(text="ok")

    async def ready(self, _: web.Request):
        if self.is_ready():
            return web.Response(text="ready")
        return web.Response(status=503, text="not ready")

    async def setup_and_start(self, port: int) -> None:
        self.runner = web.AppRunner(self)
        await self.runner.setup()

        self.site = web.TCPSite(self.runner, "0.0.0.0", port)
        await self.site.start()

