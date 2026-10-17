import os
from dataclasses import dataclass
from datetime import UTC, datetime
from enum import Enum
from typing import Awaitable, Callable

import redis.asyncio as redis
from aiohttp import ClientSession, ClientError, ClientTimeout
from redis.exceptions import RedisError
from fastapi import FastAPI, Response, Request

app = FastAPI()


REDIS_HOST = os.getenv("REDIS_HOST") or ""
REDIS_PORT = int(os.getenv("REDIS_PORT") or "")
REDIS_PASSWORD = os.getenv("REDIS_PASSWORD") or ""

BOT_HEALTH_PORT = int(os.getenv("BOT_HEALTH_PORT") or "")
TRACKERS_HEALTH_PORT = int(os.getenv("TRACKERS_HEALTH_PORT") or "")
UTILS_HEALTH_PORT = int(os.getenv("UTILS_HEALTH_PORT") or "")
WEBSITE_HEALTH_PORT = int(os.getenv("WEBSITE_HEALTH_PORT") or "")

RENDERER_HOSTNAME = os.getenv("RENDERER_HOSTNAME") or ""
SKIN_API_HOSTNAME = os.getenv("SKIN_API_HOSTNAME") or ""

API_KEY = os.getenv("HEALTH_API_KEY")
if API_KEY is None:
    raise RuntimeError("HEALTH_API_KEY is not set")


@app.get("/ready")
def is_ready():
    return Response(status_code=200)

class StatusEnum(Enum):
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"

@dataclass
class ServiceStatusInfo:
    status: StatusEnum
    is_critical: bool

@dataclass
class HealthAggregate:
    status: StatusEnum
    checked_at: str
    services: dict[str, ServiceStatusInfo]

async def get_redis_health() -> StatusEnum:
    async with redis.Redis(
        host=REDIS_HOST,
        port=REDIS_PORT,
        password=REDIS_PASSWORD,
        socket_connect_timeout=2,
        socket_timeout=2,
    ) as client:
        try:
            if await client.ping():
                return StatusEnum.HEALTHY
        except RedisError:
            pass

        return StatusEnum.UNHEALTHY

async def get_service_status(
    uri: str,
    is_service_critical: bool,
    tls_verify: bool=True,
) -> ServiceStatusInfo:
    async with ClientSession() as session:
        try:
            res = await session.get(uri, timeout=ClientTimeout(total=2), ssl=tls_verify)
            if res.status == 200:
                return ServiceStatusInfo(status=StatusEnum.HEALTHY, is_critical=is_service_critical)
        except ClientError as exc:
            print(exc)

        return ServiceStatusInfo(status=StatusEnum.UNHEALTHY, is_critical=is_service_critical)

@app.middleware("http")
async def authenticate_request(
    request: Request,
    call_next: Callable[[Request], Awaitable[Response]],
) -> Response:
    api_key = request.headers.get("X-Api-Key")
    if api_key != API_KEY:
        return Response(status_code=401)

    response = await call_next(request)
    return response

@app.get("/health")
async def get_health() -> HealthAggregate:
    services_health = {
        "bot": await get_service_status(f"http://bot:{BOT_HEALTH_PORT}/ready", True),
        "trackers": await get_service_status(f"http://trackers:{TRACKERS_HEALTH_PORT}/ready", False),
        "utils": await get_service_status(f"http://utils:{UTILS_HEALTH_PORT}/ready", False),
        "website": await get_service_status(
            f"https://website:{WEBSITE_HEALTH_PORT}/health/ready", False, tls_verify=False),
        "renderer": await get_service_status(f"{RENDERER_HOSTNAME}/ready", True),
        "skins": await get_service_status(f"{SKIN_API_HOSTNAME}/", False),
        "redis": ServiceStatusInfo(status=await get_redis_health(), is_critical=False),
    }

    total_services = len(services_health)
    healthy_services = len([s for s in services_health.values() if s.status == StatusEnum.HEALTHY])
    unhealthy_critical_services = len([
        s for s in services_health.values()
        if s.status == StatusEnum.UNHEALTHY and s.is_critical
    ])

    if unhealthy_critical_services > 0 or healthy_services == 0:
        overall_health = StatusEnum.UNHEALTHY
    elif total_services == healthy_services:
        overall_health = StatusEnum.HEALTHY
    else:
        overall_health = StatusEnum.DEGRADED

    return HealthAggregate(
        status=overall_health,
        checked_at=datetime.now(UTC).isoformat(),
        services=services_health
    )
