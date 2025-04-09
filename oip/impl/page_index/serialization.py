from typing import Optional

from oip.base.page_index.page_index import PageIndexEntry
from oip.base.util.serialization import Serializer, Deserializer


class PageIndexEntrySerializer(Serializer[PageIndexEntry]):
    def serialize(self, index_entry: PageIndexEntry) -> str:
        return f'{index_entry.page_file_path} {index_entry.page_url}'


class PageIndexEntryDeserializer(Deserializer[PageIndexEntry]):
    def deserialize(self, serialized_index_entry: str, key: Optional[str] = None) -> PageIndexEntry:
        split_str = serialized_index_entry.split()
        return PageIndexEntry(page_file_path=split_str[0], page_url=split_str[1])
