from abc import ABC, abstractmethod
from typing import Generic, Callable, Any, TypeVar

T = TypeVar('T')


class KeyExtractor(Generic[T], ABC):
    @abstractmethod
    def extract_key(self, obj: T) -> str:
        return NotImplemented


class LambdaKeyExtractor(KeyExtractor[T]):
    def __init__(self, key_extractor_func: Callable[[T], Any]):
        self._key_extractor_func = key_extractor_func

    def extract_key(self, obj: T) -> str:
        return str(self._key_extractor_func(obj))


class AttributeKeyExtractor(KeyExtractor[T]):
    def __init__(self, attribute_name: str):
        self._attribute_name = attribute_name

    def extract_key(self, obj: T) -> str:
        return str(getattr(obj, self._attribute_name))
