from oip.base.index.index import IndexEntry
from oip.impl.index.serialization import IndexEntrySerializer, IndexEntryDeserializer
from oip.impl.util.repository.key_extraction import AttributeKeyExtractor
from oip.impl.util.repository.single_file import SingleFileRepository
from oip.impl.util.util import INDEX_FILE


class IndexEntryKeyExtractor(AttributeKeyExtractor[IndexEntry]):
    def __init__(self):
        super().__init__("page_file_path")


class IndexEntrySingleFileRepository(SingleFileRepository[IndexEntry]):
    def __init__(self, file_path: str):
        super().__init__(
            file_path=file_path,
            serializer=IndexEntrySerializer(),
            deserializer=IndexEntryDeserializer(),
            key_extractor=IndexEntryKeyExtractor()
        )


DEFAULT_INDEX_ENTRY_REPOSITORY = IndexEntrySingleFileRepository(file_path=INDEX_FILE)


def default_index_entry_repository():
    return DEFAULT_INDEX_ENTRY_REPOSITORY
