from oip.base.page.page import Page
from oip.base.token.filtration import TokenFilter
from oip.base.token.normalization import TokenNormalizer
from oip.base.token.text_extraction import TextExtractor
from oip.base.token.token import PageTokens, Token
from oip.base.token.tokenization import Tokenizer
from oip.impl.token.filtration import default_token_filter
from oip.impl.token.normalization import default_token_normalizer
from oip.impl.token.text_extraction import default_text_extractor


class SimpleTokenizer(Tokenizer):
    def __init__(
            self,
            text_extractor: TextExtractor,
            normalizer: TokenNormalizer,
            filter: TokenFilter
    ):
        self._text_extractor = text_extractor
        self._normalizer = normalizer
        self._filter = filter

    def tokenize(self, page: Page) -> PageTokens:
        text = self._text_extractor.extract(page)
        tokens = [Token(token) for token in text.split()]
        normalized_tokens = [self._normalizer.normalize(token) for token in tokens]
        filtered_tokens = [token for token in normalized_tokens if self._filter.is_satisfied_by(token)]
        return PageTokens(page.url, filtered_tokens)


DEFAULT_TOKENIZER = SimpleTokenizer(
    text_extractor=default_text_extractor(),
    normalizer=default_token_normalizer(),
    filter=default_token_filter()
)


def default_tokenizer() -> SimpleTokenizer:
    return DEFAULT_TOKENIZER
