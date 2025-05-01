from typing import List

from database.select import select_from
from oip.base.lemma.lemmatization import TokenLemmatizer
from oip.base.token.normalization import TokenNormalizer
from oip.base.token.token import Token
from oip.base.token_index.token_index import TokenIndex, TokenIndexEntry
from oip.base.util.repository import Repository
from oip.impl.util.tables import PAGE_LEMMAS


class SimpleTokenIndex(TokenIndex):
    def __init__(self,
                 repository: Repository[TokenIndexEntry],
                 token_normalizer: TokenNormalizer,
                 token_lemmatizer: TokenLemmatizer):
        self._repository = repository
        self._token_normalizer = token_normalizer
        self._token_lemmatizer = token_lemmatizer

    def get_page_urls_by_token(self, token: Token) -> List[str]:
        token = self._token_normalizer.normalize(token)
        lemma = self._token_lemmatizer.lemmatize(token)

        token_index_entry = self._repository.load(lemma.value)
        if not token_index_entry:
            return list[str]()

        return token_index_entry.page_urls

    def add_entry(self, token: Token, page_url: str):
        token = self._token_normalizer.normalize(token)
        lemma = self._token_lemmatizer.lemmatize(token)

        inverted_index_entry = self._repository.load(lemma.value)
        if not inverted_index_entry:
            inverted_index_entry = TokenIndexEntry(lemma, [page_url])
        inverted_index_entry.page_urls.add(page_url)

        self._repository.save(inverted_index_entry)


class DatabaseTokenIndex(TokenIndex):
    def get_page_urls_by_token(self, token: Token) -> List[str]:
        records = (select_from(PAGE_LEMMAS)
                   .columns(PAGE_LEMMAS.page_url)
                   .where(PAGE_LEMMAS.lemma == token.value)
                   .execute())

        return list(set(record[PAGE_LEMMAS.page_url] for record in records))

    def add_entry(self, token: Token, page_url: str):
        pass


DEFAULT_TOKEN_INDEX = DatabaseTokenIndex()


def default_token_index() -> TokenIndex:
    return DEFAULT_TOKEN_INDEX
