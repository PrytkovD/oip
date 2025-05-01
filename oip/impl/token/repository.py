from typing import List, Optional

from database.aggeration import Aggregation
from database.select import select_from
from oip.base.token.token import PageTokens, Token
from oip.base.util.repository import Repository
from oip.impl.token.serialization import PageTokensSerializer, PageTokensDeserializer
from oip.impl.util.repository.file_name_transformation import PrefixSuffixFileNameTransformer
from oip.impl.util.repository.key_extraction import LambdaKeyExtractor
from oip.impl.util.repository.multi_file import MultiFileRepository
from oip.impl.util.tables import PAGE_TOKENS


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


class PageTokensDatabaseRepository(Repository[PageTokens]):
    def load(self, key: str) -> Optional[PageTokens]:
        return NotImplemented

    def save(self, obj: PageTokens):
        page_url = obj.page_url
        for token in obj.tokens:
            PAGE_TOKENS.insert({PAGE_TOKENS.page_url: page_url, PAGE_TOKENS.token: token.value})

    def load_all(self) -> List[PageTokens]:
        tokens_aggregation = Aggregation.list(PAGE_TOKENS.token)

        records = (select_from(PAGE_TOKENS)
                   .group_by(PAGE_TOKENS.page_url)
                   .aggregate(tokens_aggregation)
                   .execute())

        page_tokens = set[PageTokens]()
        for record in records:
            page_url = record[PAGE_TOKENS.page_url]
            tokens = [Token(value) for value in record[tokens_aggregation]]
            page_tokens.add(PageTokens(page_url=page_url, tokens=tokens))

        return list(page_tokens)

    def save_all(self, objs: List[PageTokens]):
        return NotImplemented


DEFAULT_PAGE_TOKENS_REPOSITORY = PageTokensDatabaseRepository()


def default_page_tokens_repository() -> Repository[PageTokens]:
    return DEFAULT_PAGE_TOKENS_REPOSITORY
