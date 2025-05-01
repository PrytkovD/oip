import math
from typing import List, Optional

from database.aggeration import Aggregation
from database.expression import Expression
from database.select import select_from
from oip.base.tf_idf.tf_idf import PageTfIdfs, TfIdf
from oip.base.util.repository import Repository
from oip.impl.tf_idf.serialization import PageTfIdfsSerializer, PageTfIdfsDeserializer
from oip.impl.util.repository.file_name_transformation import PrefixSuffixFileNameTransformer
from oip.impl.util.repository.key_extraction import LambdaKeyExtractor
from oip.impl.util.repository.multi_file import MultiFileRepository
from oip.impl.util.tables import PAGE_TOKENS, PAGE, PAGE_LEMMAS, LEMMAS_TOKENS


class PageTfIdfsKeyExtractor(LambdaKeyExtractor[PageTfIdfs]):
    def __init__(self):
        super().__init__(lambda page_tf_idfs: page_tf_idfs.page_url)


class PageTokensTfIdfsMultiFileRepository(MultiFileRepository[PageTfIdfs]):
    def __init__(self, dir_path: str):
        super().__init__(
            dir_path=dir_path,
            serializer=PageTfIdfsSerializer(),
            deserializer=PageTfIdfsDeserializer(),
            key_extractor=PageTfIdfsKeyExtractor(),
            file_name_transformer=PrefixSuffixFileNameTransformer("tokens_tf_idf_", ".txt")
        )


class PageLemmasTfIdfsMultiFileRepository(MultiFileRepository[PageTfIdfs]):
    def __init__(self, dir_path: str):
        super().__init__(
            dir_path=dir_path,
            serializer=PageTfIdfsSerializer(),
            deserializer=PageTfIdfsDeserializer(),
            key_extractor=PageTfIdfsKeyExtractor(),
            file_name_transformer=PrefixSuffixFileNameTransformer("lemmas_tf_idf_", ".txt")
        )


class PageTokensTfIdfsDatabaseRepository(Repository[PageTfIdfs]):
    def load(self, key: str) -> Optional[PageTfIdfs]:
        return NotImplemented

    def save(self, obj: PageTfIdfs):
        return NotImplemented

    def load_all(self) -> List[PageTfIdfs]:
        count = 0
        for record in select_from(PAGE).aggregate(Aggregation.count()).execute():
            count = record[Aggregation.count()]

        tf = Aggregation.count().alias('tf')
        tf_query = (select_from(PAGE_TOKENS)
                    .group_by(*PAGE_TOKENS.expressions)
                    .aggregate(tf)
                    .execute())

        df = Aggregation.count().alias('df')
        df_query = (select_from(tf_query)
                    .group_by(PAGE_TOKENS.token)
                    .aggregate(df)
                    .execute())

        idf = (Expression.function(math.log)(count / df)).alias('idf')
        tf_idf = (tf * idf).alias('tf_idf')
        tf_idf_query = (select_from(tf_query)
                        .join(df_query, PAGE_TOKENS.token, PAGE_TOKENS.token)
                        .columns(*PAGE_TOKENS.expressions, idf, tf_idf)
                        .execute())

        aggregation_dict = Aggregation.dict(PAGE_TOKENS.token, idf, tf_idf)
        dict_query = (select_from(tf_idf_query)
                      .columns(PAGE_TOKENS.page_url, aggregation_dict)
                      .group_by(*[expression.name for expression in tf_idf_query.expressions])
                      .aggregate(aggregation_dict).execute())

        aggregation_list = Aggregation.list(aggregation_dict)
        records = (select_from(dict_query)
                   .group_by(PAGE_TOKENS.page_url)
                   .aggregate(aggregation_list)
                   .execute())

        page_tf_idfs = list[PageTfIdfs]()
        for record in records:
            page_url = record[PAGE_TOKENS.page_url]
            tf_idfs = [TfIdf(dict['page_tokens.token'], dict['idf'], dict['tf_idf'])
                       for dict in record[aggregation_list]]
            page_tf_idfs.append(PageTfIdfs(page_url, tf_idfs))

        return page_tf_idfs

    def save_all(self, objs: List[PageTfIdfs]):
        return NotImplemented


DEFAULT_PAGE_TOKENS_TF_IDFS_REPOSITORY = PageTokensTfIdfsDatabaseRepository()


def default_page_tokens_tf_idfs_repository():
    return DEFAULT_PAGE_TOKENS_TF_IDFS_REPOSITORY


class PageLemmasTfIdfsDatabaseRepository(Repository[PageTfIdfs]):
    def load(self, key: str) -> Optional[PageTfIdfs]:
        return NotImplemented

    def save(self, obj: PageTfIdfs):
        return NotImplemented

    def load_all(self) -> List[PageTfIdfs]:
        count = 0
        for record in select_from(PAGE).aggregate(Aggregation.count()).execute():
            count = record[Aggregation.count()]

        tokens_per_page = Aggregation.count().alias('tokens_per_page')
        tokens_per_page_query = (select_from(PAGE_TOKENS)
                                 .group_by(PAGE_TOKENS.page_url)
                                 .aggregate(tokens_per_page)
                                 .execute())

        tokens_per_lemma = Aggregation.count().alias('tokens_per_lemma')
        tokens_per_lemma_query = (select_from(PAGE_LEMMAS)
                                  .join(LEMMAS_TOKENS, PAGE_LEMMAS.id, LEMMAS_TOKENS.lemma_id)
                                  .join(tokens_per_page_query, PAGE_LEMMAS.page_url, PAGE_TOKENS.page_url)
                                  .group_by(*PAGE_LEMMAS.expressions, tokens_per_page)
                                  .aggregate(tokens_per_lemma)
                                  .execute())

        tf = (tokens_per_lemma / tokens_per_page).alias('tf')
        tf_query = (select_from(tokens_per_lemma_query)
                    .columns(*PAGE_LEMMAS.expressions, tf)
                    .execute())

        df = Aggregation.count().alias('df')
        df_query = (select_from(tf_query)
                    .group_by(PAGE_LEMMAS.lemma)
                    .aggregate(df)
                    .execute())

        idf = (Expression.function(math.log)(count / df)).alias('idf')
        tf_idf = (Expression.raw('tf') * idf).alias('tf_idf')
        tf_idf_query = (select_from(tf_query)
                        .join(df_query, PAGE_LEMMAS.lemma, PAGE_LEMMAS.lemma)
                        .columns(PAGE_LEMMAS.page_url, PAGE_LEMMAS.lemma, idf, tf_idf)
                        .execute())

        aggregation_dict = Aggregation.dict(PAGE_LEMMAS.lemma, idf, tf_idf)
        dict_query = (select_from(tf_idf_query)
                      .columns(PAGE_LEMMAS.page_url, aggregation_dict)
                      .group_by(*[expression.name for expression in tf_idf_query.expressions])
                      .aggregate(aggregation_dict).execute())

        aggregation_list = Aggregation.list(aggregation_dict)
        records = (select_from(dict_query)
                   .group_by(PAGE_LEMMAS.page_url)
                   .aggregate(aggregation_list)
                   .execute())

        page_tf_idfs = list[PageTfIdfs]()
        for record in records:
            page_url = record[PAGE_LEMMAS.page_url]
            tf_idfs = [TfIdf(dict['page_lemmas.lemma'], dict['idf'], dict['tf_idf'])
                       for dict in record[aggregation_list]]
            page_tf_idfs.append(PageTfIdfs(page_url, tf_idfs))

        return page_tf_idfs

    def save_all(self, objs: List[PageTfIdfs]):
        return NotImplemented


DEFAULT_PAGE_LEMMAS_TF_IDFS_REPOSITORY = PageLemmasTfIdfsDatabaseRepository()


def default_page_lemmas_tf_idfs_repository():
    return DEFAULT_PAGE_LEMMAS_TF_IDFS_REPOSITORY
