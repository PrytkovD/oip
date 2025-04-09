from typing import List

from oip.base.lemma.lemmatization import TokenLemmatizer
from oip.base.token.normalization import TokenNormalizer
from oip.base.token.token import Token
from oip.base.token_index.token_index import TokenIndex, TokenIndexEntry
from oip.base.util.repository import Repository
from oip.impl.lemma.lemmatization import default_token_lemmatizer
from oip.impl.token.normalization import default_token_normalizer
from oip.impl.token_index.repository import default_token_index_entry_repository


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


DEFAULT_TOKEN_INDEX = SimpleTokenIndex(
    repository=default_token_index_entry_repository(),
    token_normalizer=default_token_normalizer(),
    token_lemmatizer=default_token_lemmatizer()
)


def default_token_index() -> TokenIndex:
    return DEFAULT_TOKEN_INDEX
