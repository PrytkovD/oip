import uuid
from typing import List, Optional

from database.select import select_from
from oip.base.page.page import Page
from oip.base.page_index.page_index import PageIndex
from oip.base.util.repository import Repository
from oip.impl.page.serialization import PageSerializer, PageDeserializer
from oip.impl.util.repository.file_name_transformation import NoopFileNameTransformer
from oip.impl.util.repository.key_extraction import AttributeKeyExtractor
from oip.impl.util.repository.multi_file import MultiFileRepository
from oip.impl.util.tables import PAGE, PAGE_CONTENT


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


class PageDatabaseRepository(Repository[Page]):
    def load(self, key: str) -> Optional[Page]:
        return NotImplemented

    def save(self, obj: Page):
        id = str(uuid.uuid4())
        PAGE.insert({PAGE.id: id, PAGE.url: obj.url})
        PAGE_CONTENT.insert({PAGE_CONTENT.page_id: id, PAGE_CONTENT.content: obj.content})

    def load_all(self) -> List[Page]:
        records = (select_from(PAGE)
                   .join(PAGE_CONTENT, PAGE.id, PAGE_CONTENT.page_id)
                   .execute())

        return list(set(Page(record[PAGE.url], record[PAGE_CONTENT.content]) for record in records))

    def save_all(self, objs: List[Page]):
        return NotImplemented


DEFAULT_PAGE_REPOSITORY = PageDatabaseRepository()


def default_page_repository() -> Repository[Page]:
    return DEFAULT_PAGE_REPOSITORY
