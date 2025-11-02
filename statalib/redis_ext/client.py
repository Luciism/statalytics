import logging
import asyncio
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


class RedisClient:
    def __init__(self) -> None:
        self._redis: redis.Redis | None = None

    @property
    def client(self) -> redis.Redis:
        if self._redis is None:
            self._redis = create_client()
        return self._redis

    async def reconnect(self, attempt: int=0) -> redis.Redis:
        max_delay = 120  # Seconds

        delay: float = min(max_delay, 0.5 * (2 ** attempt - 1))
        logging.warning(f"Attempting to reconnect to redis in: {delay} seconds")
        await asyncio.sleep(delay)

        try:
            new_client = create_client()
            await new_client.ping()
            logging.info(f"Successfully reconnected to redis.")
            self._redis = new_client
            return new_client
        except redis.ConnectionError:
            return await self.reconnect(attempt+1)


redis_client = RedisClient()

