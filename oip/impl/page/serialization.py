from typing import Optional

from oip.base.page.page import Page
from oip.base.util.serialization import Serializer, Deserializer


class PageSerializer(Serializer[Page]):
    def serialize(self, page: Page) -> str:
        return page.content


class PageDeserializer(Deserializer[Page]):
    def deserialize(self, content: str, url: Optional[str] = None) -> Page:
        return Page("ERROR" if url is None else url, content)
