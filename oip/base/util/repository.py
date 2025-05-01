from abc import ABC, abstractmethod
from typing import Generic, TypeVar, Optional, List

T = TypeVar('T')


class Repository(Generic[T], ABC):
    @abstractmethod
    def load(self, key: str) -> Optional[T]:
        return NotImplemented

    @abstractmethod
    def save(self, obj: T):
        return NotImplemented

    @abstractmethod
    def load_all(self) -> List[T]:
        return NotImplemented

    @abstractmethod
    def save_all(self, objs: List[T]):
        return NotImplemented

    def load_all_into(self, other: 'Repository[T]'):
        if type(self) is not type(other):
            other.save_all(self.load_all())
