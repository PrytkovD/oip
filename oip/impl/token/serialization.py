from typing import Optional

from oip.base.token.token import PageTokens, Token
from oip.base.util.serialization import Serializer, Deserializer


class TokenSerializer(Serializer[Token]):
    def serialize(self, token: Token) -> str:
        return token.value


class TokenDeserializer(Deserializer[Token]):
    def deserialize(self, serialized_token: str, key: Optional[str] = None) -> Token:
        return Token(serialized_token.strip())


class PageTokensSerializer(Serializer[PageTokens]):
    def __init__(self):
        self._token_serializer = TokenSerializer()

    def serialize(self, page_tokens: PageTokens) -> str:
        return '\n'.join([self._token_serializer.serialize(token) for token in sorted(page_tokens.tokens)])


class PageTokensDeserializer(Deserializer[PageTokens]):
    def __init__(self):
        self._token_deserializer = TokenDeserializer()

    def deserialize(self, serialized_page_tokens: str, key: Optional[str] = None) -> PageTokens:
        tokens = [self._token_deserializer.deserialize(value) for value in serialized_page_tokens.strip().split('\n')]
        return PageTokens(page_url=key, tokens=tokens)
