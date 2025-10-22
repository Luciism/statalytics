import os
import redis.asyncio as redis

def create_client() -> redis.Redis:
    host = os.getenv("REDIS_HOST")
    port = os.getenv("REDIS_PORT")
    
    assert host is not None, "'REDIS_HOST' environment variable is unset"
    assert port is not None, "'REDIS_PORT' environment variable is unset"

    try:
        port = int(port)
    except ValueError as exc:
        raise ValueError("REDIS_PORT environment variable is not a valid integer") from exc

    return redis.Redis(
        host=host,
        port=port,
        password=os.getenv("REDIS_PASSWORD"),
        decode_responses=True
    )
