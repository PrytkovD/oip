from oip.base.token.token import PageTokens
from oip.base.util.repository import Repository
from oip.impl.token.serialization import PageTokensSerializer, PageTokensDeserializer
from oip.impl.util.repository.file_name_transformation import PrefixSuffixFileNameTransformer
from oip.impl.util.repository.key_extraction import LambdaKeyExtractor
from oip.impl.util.repository.multi_file import MultiFileRepository
from oip.impl.util.util import TOKENS_DIR


class PageTokensKeyExtractor(LambdaKeyExtractor[PageTokens]):
    def __init__(self):
        super().__init__(lambda page_tokens: page_tokens.page_url)


class PageTokensMultiFileRepository(MultiFileRepository[PageTokens]):
    def __init__(self, dir_path: str):
        super().__init__(
            dir_path=dir_path,
            serializer=PageTokensSerializer(),
            deserializer=PageTokensDeserializer(),
            key_extractor=PageTokensKeyExtractor(),
            file_name_transformer=PrefixSuffixFileNameTransformer("tokens_", ".txt")
        )


DEFAULT_PAGE_TOKENS_REPOSITORY = PageTokensMultiFileRepository(dir_path=TOKENS_DIR)


def default_page_tokens_repository() -> Repository[PageTokens]:
    return DEFAULT_PAGE_TOKENS_REPOSITORY
