from typing import Optional

from oip.base.lemma.lemma import PageLemmas, Lemma
from oip.base.util.serialization import Serializer, Deserializer
from oip.impl.token.serialization import TokenSerializer, TokenDeserializer


class LemmaSerializer(Serializer[Lemma]):
    def __init__(self):
        self._token_serializer = TokenSerializer()

    def serialize(self, lemma: Lemma) -> str:
        serialized_lemma = self._token_serializer.serialize(lemma.lemma)
        serialized_tokens = ' '.join([self._token_serializer.serialize(token) for token in lemma.tokens])
        return f"{serialized_lemma}: {serialized_tokens}"


class LemmaDeserializer(Deserializer[Lemma]):
    def __init__(self):
        self._token_deserializer = TokenDeserializer()

    def deserialize(self, serialized_lemma: str, key: Optional[str] = None) -> Lemma:
        serialized_lemma, serialized_tokens = serialized_lemma.split(':')
        lemma = self._token_deserializer.deserialize(serialized_lemma.strip())
        serialized_tokens = serialized_tokens.split()
        tokens = [self._token_deserializer.deserialize(token.strip()) for token in serialized_tokens]
        return Lemma(lemma, tokens)


class PageLemmasSerializer(Serializer[PageLemmas]):
    def __init__(self):
        self._lemma_serializer = LemmaSerializer()

    def serialize(self, page_lemmas: PageLemmas) -> str:
        return '\n'.join([self._lemma_serializer.serialize(lemma) for lemma in page_lemmas.lemmas])


class PageLemmasDeserializer(Deserializer[PageLemmas]):
    def __init__(self):
        self._lemma_deserializer = LemmaDeserializer()

    def deserialize(self, serialized_page_lemmas: str, key: Optional[str] = None) -> PageLemmas:
        lemmas = [self._lemma_deserializer.deserialize(value) for value in serialized_page_lemmas.strip().split('\n')]
        return PageLemmas(page_url=key, lemmas=lemmas)
