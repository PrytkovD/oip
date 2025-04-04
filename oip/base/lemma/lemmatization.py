from abc import ABC, abstractmethod

from oip.base.lemma.lemma import PageLemmas
from oip.base.token.token import PageTokens, Token


class Lemmatizer(ABC):
    @abstractmethod
    def lemmatize(self, page_tokens: PageTokens) -> PageLemmas:
        return NotImplemented


class TokenLemmatizer(ABC):
    @abstractmethod
    def lemmatize_token(self, token: Token) -> Token:
        return NotImplemented
