from oip.base.page_index.page_index import PageIndex
from oip.base.page.page import Page
from oip.base.util.repository import Repository
from oip.impl.page_index.page_index import default_page_index
from oip.impl.page.serialization import PageSerializer, PageDeserializer
from oip.impl.util.repository.file_name_transformation import NoopFileNameTransformer
from oip.impl.util.repository.key_extraction import AttributeKeyExtractor
from oip.impl.util.repository.multi_file import MultiFileRepository
from oip.impl.util.util import PAGES_DIR


class PageKeyExtractor(AttributeKeyExtractor[Page]):
    def __init__(self):
        super().__init__("url")


class PageMultiFileRepository(MultiFileRepository[Page]):
    def __init__(self, dir_path: str, index: PageIndex):
        super().__init__(
            dir_path=dir_path,
            serializer=PageSerializer(),
            deserializer=PageDeserializer(),
            key_extractor=PageKeyExtractor(),
            file_name_transformer=NoopFileNameTransformer()
        )
        self._index = index

    def save(self, page: Page):
        super().save(page)
        file_path = self.get_file_path_by_key(page.url)
        self._index.add_entry(page.url, file_path)


DEFAULT_PAGE_REPOSITORY = PageMultiFileRepository(
    dir_path=PAGES_DIR,
    index=default_page_index()
)


def default_page_repository() -> Repository[Page]:
    return DEFAULT_PAGE_REPOSITORY
