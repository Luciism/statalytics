"""Redis streams read / write functionality."""

import asyncio
import logging
import socket
import uuid
from collections.abc import Awaitable
from typing import Callable

import redis.asyncio as redis
from redis.typing import EncodableT, FieldT

from .models import DeserializationError, PriorityLog, SubscriptionUpdate
from .models import Deserializable, T
from .client import create_client


class RedisStreamProducer:
    """Methods for appending to a redis stream."""

    def __init__(self, client: redis.Redis) -> None:
        """
        Create new redis producer instance.

        :param client: An async redis client to act with.
        """
        self._client: redis.Redis = client

    async def add_subscription_update(self, purchase: SubscriptionUpdate) -> None:
        """Append a `SubscriptionUpdate` to the `subscription_updates` stream."""
        await self.append_to_stream("subscription_updates", purchase.serialize())

    async def add_priority_log(self, log: PriorityLog) -> None:
        """Append a `PriorityLog` to the `priority_logs` stream."""
        await self.append_to_stream("priority_logs", log.serialize())

    async def append_to_stream(
        self, stream_name: str, item: dict[FieldT, EncodableT]
    ) -> None:
        """
        Append a dictionary object to a given stream.

        :param stream_name: The name of the stream to append to.
        :param item: A redis-compatible dictionary to append.
        """
        await self._client.xadd(stream_name, item)


class RedisStreamConsumer:
    """Methods for consuming a redis stream."""

    def __init__(self, client: redis.Redis) -> None:
        """
        Create new redis consumer instance.

        :param client: An async redis client to act with.
        """
        self._client: redis.Redis = client
        self._consumer_name: str = f"{socket.gethostname()}-{uuid.uuid4()}"
        self._is_reconnecting: bool = False

    async def read_subscription_updates_stream(
        self, handler: Callable[[SubscriptionUpdate], Awaitable[None]]
    ) -> None:
        """
        Recursively read any messages appended to the `subscription_updates` stream.
        **WARNING**: This function does not return, it should be spawned as a task.

        :param handler: An async function that handles messages from the stream.
        """
        await self.read_stream("subscription_updates", SubscriptionUpdate, handler)

    async def read_priority_log_stream(
        self, handler: Callable[[PriorityLog], Awaitable[None]]
    ) -> None:
        """
        Recursively read any messages appended to the `priority_logs` stream.
        **WARNING**: This function does not return, it should be spawned as a task.

        :param handler: An async function that handles messages from the stream.
        """
        await self.read_stream("priority_logs", PriorityLog, handler)

    async def _read_stream(
        self,
        stream_name: str,
        model: Deserializable[T],
        handler: Callable[[T], Awaitable[None]],
    ) -> None:
        try:
            await self._client.xgroup_create(
                stream_name, f"{stream_name}_group", id="0", mkstream=True
            )
            await self._client.xgroup_create(
                f"{stream_name}_dead", f"{stream_name}_dead_group", id="0", mkstream=True
            )
        except redis.ResponseError:
            pass  # group already exists

        while True:
            # Read new messages for this consumer
            # TODO: handle disconnects: redis.exceptions.ConnectionError
            msgs: list[tuple[str, list[tuple[str, dict[str, str]]]]] = (
                await self._client.xreadgroup(
                    f"{stream_name}_group",
                    self._consumer_name,
                    {stream_name: ">"},
                    count=1,
                    block=0,
                )
            )

            for _, messages in msgs:
                for msg_id, fields in messages:
                    try:
                        deserialized = model.deserialize(fields)
                        await self._client.xack(
                            stream_name, f"{stream_name}_group", msg_id
                        )
                        await handler(deserialized)
                    except DeserializationError as e:
                        logging.error(f"Stream '{stream_name}' - failed to deserialize response:", exc_info=e)
                        await self._client.xadd(f"{stream_name}_dead", fields)
                        await self._client.xack(
                            stream_name, f"{stream_name}_group", msg_id
                        )

    async def read_stream(
        self,
        stream_name: str,
        model: Deserializable[T],
        handler: Callable[[T], Awaitable[None]],
    ) -> None:
        """
        Recursively read any messages appended to the given stream.
        **WARNING**: This function does not return, it should be spawned as a task.

        :param stream_name: The name of the stream to read from.
        :param model: The model class to deserialize the message into.
        :param handler: An async function that handles messages from the stream.
        """
        try:
            await self._read_stream(stream_name, model, handler)
        except redis.ConnectionError:
            conn = self._client.connection
            if (conn and not conn.is_connected or not conn) and not self._is_reconnecting:
                self._is_reconnecting = True
                self._client = await _reconnect_to_redis()
                self._is_reconnecting = False
            else:
                await asyncio.sleep(1)

            await self.read_stream(stream_name, model, handler)


async def _reconnect_to_redis(attempt: int=0) -> redis.Redis:
    max_delay = 120  # Seconds

    delay: float = min(max_delay, 0.5 * (2 ** attempt - 1))
    logging.warning(f"Attempting to reconnect to redis in: {delay} seconds")
    await asyncio.sleep(delay)

    try:
        new_client = create_client()
        await new_client.ping()
        logging.info(f"Successfully reconnected to redis.")
        return new_client
    except redis.ConnectionError:
        return await _reconnect_to_redis(attempt+1)

