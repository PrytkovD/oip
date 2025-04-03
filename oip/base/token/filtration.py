from abc import ABC, abstractmethod
from typing import List

from oip.base.token.token import Token


class TokenFilter(ABC):
    @abstractmethod
    def is_satisfied_by(self, token: Token) -> bool:
        return NotImplemented


class AllTokenFilter(TokenFilter):
    def __init__(self, filters: List[TokenFilter]):
        self._filters = filters

    def is_satisfied_by(self, token: Token) -> bool:
        return all([token_filter.is_satisfied_by(token) for token_filter in self._filters])
