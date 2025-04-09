from typing import Optional

from oip.base.token_index.token_index import TokenIndexEntry
from oip.base.util.serialization import Serializer, Deserializer
from oip.impl.token.serialization import TokenSerializer, TokenDeserializer


class InvertedIndexEntrySerializer(Serializer[TokenIndexEntry]):
    def __init__(self):
        self._token_serializer = TokenSerializer()

    def serialize(self, inverted_index_entry: TokenIndexEntry) -> str:
        serialized_lemma = self._token_serializer.serialize(inverted_index_entry.lemma)
        serialized_page_urls = ' '.join(inverted_index_entry.page_urls)
        return f"{serialized_lemma}: {serialized_page_urls}"


class InvertedIndexEntryDeserializer(Deserializer[TokenIndexEntry]):
    def __init__(self):
        self._token_deserializer = TokenDeserializer()

    def deserialize(self, serialized_inverted_index_entry: str, key: Optional[str] = None) -> TokenIndexEntry:
        serialized_lemma, serialized_page_urls = serialized_inverted_index_entry.split(':', 1)
        lemma = self._token_deserializer.deserialize(serialized_lemma.strip())
        serialized_page_urls = serialized_page_urls.split()
        page_urls = [serialized_page_url.strip() for serialized_page_url in serialized_page_urls]
        return TokenIndexEntry(lemma, page_urls)
