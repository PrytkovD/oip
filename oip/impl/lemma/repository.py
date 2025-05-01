import uuid
from typing import List, Optional

from database.aggeration import Aggregation
from database.expression import Expression
from database.select import select_from
from oip.base.lemma.lemma import PageLemmas, Lemma
from oip.base.token.token import Token
from oip.base.util.repository import Repository
from oip.impl.lemma.serialization import PageLemmasSerializer, PageLemmasDeserializer
from oip.impl.util.repository.file_name_transformation import PrefixSuffixFileNameTransformer
from oip.impl.util.repository.key_extraction import AttributeKeyExtractor
from oip.impl.util.repository.multi_file import MultiFileRepository
from oip.impl.util.tables import PAGE_LEMMAS, LEMMAS_TOKENS


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


class PageLemmasDatabaseRepository(Repository[PageLemmas]):
    def load(self, key: str) -> Optional[PageLemmas]:
        return NotImplemented

    def save(self, obj: PageLemmas):
        page_url = obj.page_url

        for lemma in obj.lemmas:
            id = str(uuid.uuid4())

            PAGE_LEMMAS.insert({
                PAGE_LEMMAS.id: id,
                PAGE_LEMMAS.page_url: page_url,
                PAGE_LEMMAS.lemma: lemma.lemma.value
            })

            for token in lemma.tokens:
                LEMMAS_TOKENS.insert({LEMMAS_TOKENS.lemma_id: id, LEMMAS_TOKENS.token: token.value})

    def load_all(self) -> List[PageLemmas]:
        tokens_aggregation = Aggregation.list(LEMMAS_TOKENS.token).alias('tokens')

        subquery1 = (select_from(PAGE_LEMMAS)
                     .join(LEMMAS_TOKENS, PAGE_LEMMAS.id, LEMMAS_TOKENS.lemma_id)
                     .group_by(PAGE_LEMMAS.id, PAGE_LEMMAS.page_url, PAGE_LEMMAS.lemma)
                     .aggregate(tokens_aggregation)
                     .execute())

        lemma_aggregation = Aggregation.dict(PAGE_LEMMAS.lemma, tokens_aggregation).alias('lemma')

        subquery2 = (select_from(subquery1)
                     .group_by(PAGE_LEMMAS.id, PAGE_LEMMAS.page_url)
                     .aggregate(lemma_aggregation)
                     .execute())

        lemmas_aggregation = Aggregation.list(lemma_aggregation).alias('lemmas')

        records = (select_from(subquery2)
                   .group_by(PAGE_LEMMAS.page_url)
                   .aggregate(lemmas_aggregation)
                   .execute())

        page_lemmas = set[PageLemmas]()
        for record in records:
            page_url = record[PAGE_LEMMAS.page_url]
            lemmas = record[lemmas_aggregation]
            lemmas = [Lemma(Token(lemma[PAGE_LEMMAS.lemma.name]),
                            [Token(token) for token in lemma['tokens']])
                      for lemma in lemmas]
            page_lemmas.add(PageLemmas(page_url, lemmas))

        return list(page_lemmas)

    def save_all(self, objs: List[PageLemmas]):
        return NotImplemented


DEFAULT_PAGE_LEMMAS_REPOSITORY = PageLemmasDatabaseRepository()


def default_page_lemmas_repository() -> Repository[PageLemmas]:
    return DEFAULT_PAGE_LEMMAS_REPOSITORY
