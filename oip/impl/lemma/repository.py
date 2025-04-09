from oip.base.lemma.lemma import PageLemmas
from oip.base.util.repository import Repository
from oip.impl.lemma.serialization import PageLemmasSerializer, PageLemmasDeserializer
from oip.impl.util.repository.file_name_transformation import PrefixSuffixFileNameTransformer
from oip.impl.util.repository.key_extraction import AttributeKeyExtractor
from oip.impl.util.repository.multi_file import MultiFileRepository
from oip.impl.util.util import LEMMAS_DIR


class PageLemmasKeyExtractor(AttributeKeyExtractor[PageLemmas]):
    def __init__(self):
        super().__init__("page_url")


class PageLemmasMultiFileRepository(MultiFileRepository[PageLemmas]):
    def __init__(self, dir_path: str):
        super().__init__(
            dir_path=dir_path,
            serializer=PageLemmasSerializer(),
            deserializer=PageLemmasDeserializer(),
            key_extractor=PageLemmasKeyExtractor(),
            file_name_transformer=PrefixSuffixFileNameTransformer("lemmas_", ".txt")
        )


DEFAULT_PAGE_LEMMAS_REPOSITORY = PageLemmasMultiFileRepository(dir_path=LEMMAS_DIR)


def default_page_lemmas_repository() -> Repository[PageLemmas]:
    return DEFAULT_PAGE_LEMMAS_REPOSITORY
