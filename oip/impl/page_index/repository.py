from oip.base.page_index.page_index import PageIndexEntry
from oip.impl.page_index.serialization import PageIndexEntrySerializer, PageIndexEntryDeserializer
from oip.impl.util.repository.key_extraction import AttributeKeyExtractor
from oip.impl.util.repository.single_file import SingleFileRepository
from oip.impl.util.util import PAGE_INDEX_FILE


class PageIndexEntryKeyExtractor(AttributeKeyExtractor[PageIndexEntry]):
    def __init__(self):
        super().__init__("page_url")


class PageIndexEntrySingleFileRepository(SingleFileRepository[PageIndexEntry]):
    def __init__(self, file_path: str):
        super().__init__(
            file_path=file_path,
            serializer=PageIndexEntrySerializer(),
            deserializer=PageIndexEntryDeserializer(),
            key_extractor=PageIndexEntryKeyExtractor()
        )


DEFAULT_PAGE_INDEX_ENTRY_REPOSITORY = PageIndexEntrySingleFileRepository(file_path=PAGE_INDEX_FILE)


def default_page_index_entry_repository():
    return DEFAULT_PAGE_INDEX_ENTRY_REPOSITORY
