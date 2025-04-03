import os
from typing import Optional, List
from typing import TypeVar

from oip.base.util.repository import Repository
from oip.base.util.serialization import Serializer, Deserializer
from oip.impl.util.repository.key_extraction import KeyExtractor

T = TypeVar('T')

class SingleFileRepository(Repository[T]):
    def __init__(self,
                 file_path: str,
                 serializer: Serializer[T],
                 deserializer: Deserializer[T],
                 key_extractor: KeyExtractor[T]):
        self._file_path = file_path
        self._serializer = serializer
        self._deserializer = deserializer
        self._key_extractor = key_extractor

        dir_path = os.path.dirname(self._file_path)
        if dir_path:
            os.makedirs(dir_path, exist_ok=True)

    def load(self, key: str) -> Optional[T]:
        if not os.path.exists(self._file_path):
            return None

        with open(self._file_path, 'r') as file:
            for line in file:
                serialized_obj = line.strip()
                if not serialized_obj:
                    continue
                obj = self._deserializer.deserialize(serialized_obj)
                obj_key = self._key_extractor.extract_key(obj)
                if obj_key == key:
                    return obj

        return None

    def save(self, obj: T):
        self.save_all([obj])

    def load_all(self) -> List[T]:
        if not os.path.exists(self._file_path):
            return list[T]()

        objs = list[T]()

        with open(self._file_path, 'r') as file:
            for line in file:
                serialized_obj = line.strip()
                if not serialized_obj:
                    continue
                obj = self._deserializer.deserialize(serialized_obj)
                objs.append(obj)

        return objs

    def save_all(self, objs: List[T]):
        saved_objs = self.load_all()
        objs_to_save = {self._key_extractor.extract_key(obj): obj for obj in saved_objs}

        for obj in objs:
            key = self._key_extractor.extract_key(obj)
            objs_to_save[key] = obj

        with open(self._file_path, 'w') as file:
            for obj in objs_to_save.values():
                serialized_obj = self._serializer.serialize(obj)
                if not serialized_obj:
                    continue
                file.write(serialized_obj + '\n')
