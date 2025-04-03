from abc import ABC, abstractmethod

from oip.base.token.token import Token


class TokenNormalizer(ABC):
    @abstractmethod
    def normalize(self, token: Token) -> Token:
        return NotImplemented
