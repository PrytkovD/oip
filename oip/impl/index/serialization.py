from typing import Optional

from oip.base.index.index import IndexEntry
from oip.base.util.serialization import Serializer, Deserializer


class IndexEntrySerializer(Serializer[IndexEntry]):
    def serialize(self, index_entry: IndexEntry) -> str:
        return f'{index_entry.page_file_path} {index_entry.page_url}'


class IndexEntryDeserializer(Deserializer[IndexEntry]):
    def deserialize(self, serialized_index_entry: str, key: Optional[str] = None) -> IndexEntry:
        split_str = serialized_index_entry.split()
        return IndexEntry(page_file_path=split_str[0], page_url=split_str[1])
