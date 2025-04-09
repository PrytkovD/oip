import nltk
from nltk.corpus import words, stopwords

from oip.base.token.filtration import TokenFilter, AllTokenFilter
from oip.base.token.token import Token


class MinLenTokenFilter(TokenFilter):
    def __init__(self, min_len: int = 0):
        self._min_len = min_len

    def is_satisfied_by(self, token: Token) -> bool:
        return len(token.value) >= self._min_len


class NltkTokenFilter(TokenFilter):
    def __init__(self):
        super().__init__()
        nltk.download('words', quiet=True)
        nltk.download('stopwords', quiet=True)
        self._allowed_words = set(words.words())
        self._stop_words = set(stopwords.words())

    def is_satisfied_by(self, token: Token) -> bool:
        return token.value in self._allowed_words and token.value not in self._stop_words


DEFAULT_TOKEN_FILTER = AllTokenFilter([
    MinLenTokenFilter(min_len=2),
    NltkTokenFilter()
])


def default_token_filter() -> TokenFilter:
    return DEFAULT_TOKEN_FILTER
