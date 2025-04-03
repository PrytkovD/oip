import os
from typing import Optional, List
from typing import TypeVar

from oip.base.util.repository import Repository
from oip.base.util.serialization import Serializer, Deserializer
from oip.impl.util.repository.file_name_transformation import FileNameTransformer
from oip.impl.util.repository.key_extraction import KeyExtractor
from oip.impl.util.util import quote, unquote

T = TypeVar('T')


class MultiFileRepository(Repository[T]):
    def __init__(self,
                 dir_path: str,
                 serializer: Serializer[T],
                 deserializer: Deserializer[T],
                 key_extractor: KeyExtractor[T],
                 file_name_transformer: FileNameTransformer):
        self._dir_path = dir_path
        self._serializer = serializer
        self._deserializer = deserializer
        self._key_extractor = key_extractor
        self._file_name_transformer = file_name_transformer

        os.makedirs(self._dir_path, exist_ok=True)

    def load(self, key: str) -> Optional[T]:
        file_path = self.get_file_path_by_key(key)

        if not os.path.isfile(file_path):
            return None

        with open(file_path, 'r') as f:
            serialized_obj = f.read()
            return self._deserializer.deserialize(serialized_obj, key)

    def save(self, obj: T):
        key = self._key_extractor.extract_key(obj)
        file_path = self.get_file_path_by_key(key)
        serialized_obj = self._serializer.serialize(obj)

        with open(file_path, 'w') as f:
            f.write(serialized_obj)

    def load_all(self) -> List[T]:
        objs = list[T]()

        for file_name in os.listdir(self._dir_path):
            key = self.get_key_by_file_path(file_name)
            obj = self.load(key)
            if not obj:
                continue
            objs.append(obj)

        return objs

    def save_all(self, objs: List[T]):
        for obj in objs:
            self.save(obj)

    def get_file_path_by_key(self, key: str) -> str:
        file_name = quote(key)
        file_name = self._file_name_transformer.apply_transformation(file_name)
        file_path = os.path.join(self._dir_path, file_name)
        return file_path

    def get_key_by_file_path(self, file_path: str) -> str:
        file_name = os.path.basename(file_path)
        file_name = self._file_name_transformer.revert_transformation(file_name)
        key = unquote(file_name)
        return key
