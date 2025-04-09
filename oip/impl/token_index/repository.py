from oip.base.token_index.token_index import TokenIndexEntry
from oip.base.util.repository import Repository
from oip.impl.token_index.serialization import InvertedIndexEntrySerializer, InvertedIndexEntryDeserializer
from oip.impl.util.repository.key_extraction import LambdaKeyExtractor
from oip.impl.util.repository.partitioned_file import PartitionedFileRepository
from oip.impl.util.util import TOKEN_INDEX_FILE


class TokenIndexEntryKeyExtractor(LambdaKeyExtractor[TokenIndexEntry]):
    def __init__(self):
        super().__init__(lambda inverted_index_entry: inverted_index_entry.lemma.value)


class TokenIndexEntryPartitionedFileRepository(PartitionedFileRepository[TokenIndexEntry]):
    def __init__(self, file_path: str):
        super().__init__(
            file_path=file_path,
            serializer=InvertedIndexEntrySerializer(),
            deserializer=InvertedIndexEntryDeserializer(),
            key_extractor=TokenIndexEntryKeyExtractor()
        )


DEFAULT_TOKEN_INDEX_ENTRY_REPOSITORY = TokenIndexEntryPartitionedFileRepository(file_path=TOKEN_INDEX_FILE)


def default_token_index_entry_repository() -> Repository[TokenIndexEntry]:
    return DEFAULT_TOKEN_INDEX_ENTRY_REPOSITORY
