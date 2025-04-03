from oip.base.index.index import IndexEntry
from oip.base.page.page import Page
from oip.base.util.repository import Repository
from oip.impl.index.repository import default_index_entry_repository
from oip.impl.page.serialization import PageSerializer, PageDeserializer
from oip.impl.util.repository.file_name_transformation import NoopFileNameTransformer
from oip.impl.util.repository.key_extraction import AttributeKeyExtractor
from oip.impl.util.repository.multi_file import MultiFileRepository
from oip.impl.util.util import PAGES_DIR


class PageKeyExtractor(AttributeKeyExtractor[Page]):
    def __init__(self):
        super().__init__("url")


class PageMultiFileRepository(MultiFileRepository[Page]):
    def __init__(self, dir_path: str, index_entry_repository: Repository[IndexEntry]):
        super().__init__(
            dir_path=dir_path,
            serializer=PageSerializer(),
            deserializer=PageDeserializer(),
            key_extractor=PageKeyExtractor(),
            file_name_transformer=NoopFileNameTransformer()
        )
        self._index_entry_repository = index_entry_repository

    def save(self, page: Page):
        super().save(page)
        file_path = self.get_file_path_by_key(page.url)
        index_entry = IndexEntry(file_path, page.url)
        self._index_entry_repository.save(index_entry)


DEFAULT_PAGE_REPOSITORY = PageMultiFileRepository(
    dir_path=PAGES_DIR,
    index_entry_repository=default_index_entry_repository()
)


def default_page_repository() -> Repository[Page]:
    return DEFAULT_PAGE_REPOSITORY
