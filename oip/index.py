from abc import ABC
from typing import List, Optional

from oip.repository import Repository
from oip.serialization import Serializer, Deserializer
from oip.util import INDEX_FILE


class IndexEntry:
    def __init__(self, page_file_path: str, page_url: str):
        self.page_file_path = page_file_path
        self.page_url = page_url


class IndexEntrySerializer(Serializer[IndexEntry]):
    def serialize(self, index_entry: IndexEntry) -> str:
        return f'{index_entry.page_file_path} {index_entry.page_url}'


class IndexEntryDeserializer(Deserializer[IndexEntry]):
    def deserialize(self, serialized_index_entry: str) -> IndexEntry:
        split = serialized_index_entry.split()
        return IndexEntry(page_file_path=split[0].strip(), page_url=split[1].strip())


class IndexEntryRepository(Repository[IndexEntry], ABC):
    pass


class FileIndexEntryRepository(IndexEntryRepository):
    def __init__(self):
        self._deserializer = IndexEntryDeserializer()
        self._serializer = IndexEntrySerializer()

    def load(self, key: str) -> Optional[IndexEntry]:
        return NotImplemented

    def load_all(self) -> List[IndexEntry]:
        index_entries = list[IndexEntry]()
        with open(INDEX_FILE, 'r', encoding='utf-8') as file:
            for line in file.readlines():
                index_entry = self._deserializer.deserialize(line)
                index_entries.append(index_entry)
        return index_entries

    def save(self, index_entry: IndexEntry) -> IndexEntry:
        with open(INDEX_FILE, 'a', encoding='utf-8') as file:
            file.write(f'{self._serializer.serialize(index_entry)}\n')
