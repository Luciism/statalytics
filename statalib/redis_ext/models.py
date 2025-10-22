"""Data models that can be written / read to and from a redis stream."""

from typing import Generic, TypeVar, Protocol, Any
from dataclasses import dataclass
from enum import Enum
from redis.typing import EncodableT, FieldT 


T = TypeVar("T", covariant=True)

class Codec(Protocol[T]):
    def serialize(self) -> dict[str | FieldT, str | EncodableT]: ...

    @staticmethod
    def deserialize(fields: dict[str, Any]) -> T: ...


class Deserializable(Protocol[T]):
    @staticmethod
    def deserialize(fields: dict[str, Any]) -> T: ...

class DeserializationError(Exception):
    """JSON Deserialization to dataclass failed."""


@dataclass
class SubscriptionUpdate:
    """Denotes a user's subscription has been updated."""
    user_id: int 

    def serialize(self) -> dict[FieldT, EncodableT]:
        """Serialize the model to a dictionary."""
        return {"user_id": self.user_id}

    @staticmethod
    def deserialize(fields: dict[str, int]) -> 'SubscriptionUpdate':
        """Deserialize a dictionary into the model."""
        try:
            return SubscriptionUpdate(user_id=fields["user_id"])
        except (KeyError, UnicodeDecodeError) as exc:
            raise DeserializationError from exc


class LogPriority(Enum):
    """Priorities of a priority log."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class PriorityLog:
    """A log with a given priority that can be acted upon accordingly."""
    priority: LogPriority
    """The priority of the log."""
    type: str
    """The log type, used to determine actions."""
    content: str
    """The log message content."""

    def serialize(self) -> dict[FieldT, EncodableT]:
        """Serialize the model to a dictionary."""
        return {
            "priority": self.priority.value,
            "type": self.type,
            "content": self.content,
        }

    @staticmethod
    def deserialize(fields: dict[str, str]) -> 'PriorityLog':
        """Deserialize a dictionary into the model."""
        try:
            return PriorityLog(
                priority=LogPriority(fields["priority"]),
                type=fields["type"],
                content=fields["content"],
            )
        except (KeyError, UnicodeDecodeError) as exc:
            raise DeserializationError from exc


@dataclass
class DispatchableEvent(Generic[T]):
    event_name: str
    item: Codec[T]

    def serialize(self) -> dict[FieldT, EncodableT]:
        """Serialize the model to a dictionary."""
        return {
            "event_name": self.event_name,
            "item": self.item.serialize()
        }

    @staticmethod
    def deserialize(fields: dict[str, str], codec_type: type[Codec[T]]) -> 'DispatchableEvent[T]':
        """Deserialize a dictionary into the model."""
        try:
            return DispatchableEvent(
                event_name=fields["event_name"],
                item=codec_type.deserialize(fields["item"])
            )
        except (KeyError, UnicodeDecodeError) as exc:
            raise DeserializationError from exc
