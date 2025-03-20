from abc import ABC, abstractmethod
from typing import Generic, TypeVar

T = TypeVar('T')


class Serializer(Generic[T], ABC):
    @abstractmethod
    def serialize(self, obj: T) -> str:
        return NotImplemented


class Deserializer(Generic[T], ABC):
    @abstractmethod
    def deserialize(self, obj: str) -> T:
        return NotImplemented
