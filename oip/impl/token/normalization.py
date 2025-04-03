from oip.base.token.normalization import TokenNormalizer
from oip.base.token.token import Token


class LowercaseTokenNormalizer(TokenNormalizer):
    def normalize(self, token: Token) -> Token:
        return Token(token.value.strip().lower())


DEFAULT_TOKEN_NORMALIZER = LowercaseTokenNormalizer()


def default_token_normalizer() -> TokenNormalizer:
    return DEFAULT_TOKEN_NORMALIZER
