from typing import Optional

from oip.base.tf_idf.tf_idf import TfIdf, PageTfIdfs
from oip.base.util.serialization import Serializer, Deserializer


class TfIdfSerializer(Serializer[TfIdf]):
    def serialize(self, tf_idf: TfIdf) -> str:
        return f'{tf_idf.token} {tf_idf.idf} {tf_idf.tf_idf}'


class TfIdfDeserializer(Deserializer[TfIdf]):
    def deserialize(self, serialized_tf_idf: str, key: Optional[str] = None) -> TfIdf:
        token, idf, tf_idf = serialized_tf_idf.strip().split()
        return TfIdf(token, float(idf), float(tf_idf))


class PageTfIdfsSerializer(Serializer[PageTfIdfs]):
    def __init__(self):
        self._tf_idf_serializer = TfIdfSerializer()

    def serialize(self, page_tf_idfs: PageTfIdfs) -> str:
        return '\n'.join([self._tf_idf_serializer.serialize(tf_idf) for tf_idf in sorted(page_tf_idfs.tf_idfs)])


class PageTfIdfsDeserializer(Deserializer[PageTfIdfs]):
    def __init__(self):
        self._tf_idf_deserializer = TfIdfDeserializer()

    def deserialize(self, serialized_page_tf_idfs: str, key: Optional[str] = None) -> PageTfIdfs:
        tf_idfs = [self._tf_idf_deserializer.deserialize(value) for value in
                   serialized_page_tf_idfs.strip().split('\n')]
        return PageTfIdfs(page_url=key, tf_idfs=tf_idfs)
