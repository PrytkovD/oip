from typing import Optional, List, TypeVar

from oip.base.util import Repository
from oip.impl.util.repository import KeyExtractor

T = TypeVar('T')


class ImMemoryRepository(Repository[T]):
    def __init__(self, key_extractor: KeyExtractor[T]):
        self._data = dict[str, T]()
        self._key_extractor = key_extractor

    def load(self, key: str) -> Optional[T]:
        return self._data[key]

    def save(self, obj: T):
        key = self._key_extractor.extract_key(obj)
        self._data[key] = obj

    def load_all(self) -> List[T]:
        return list(self._data.values())

    def save_all(self, objs: List[T]):
        for obj in objs:
            self.save(obj)
