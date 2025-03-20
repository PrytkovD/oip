from abc import ABC
from os import makedirs, listdir
from os.path import join, isfile
from typing import Optional, List

from oip.repository import Repository
from oip.serialization import Serializer, Deserializer
from oip.util import PAGES_DIR, url_to_file_path, file_path_to_url


class Page:
    def __init__(self, url: Optional[str], content: str):
        self.url = url
        self.content = content


class PageSerializer(Serializer[Page]):
    def serialize(self, page: Page) -> str:
        return page.content


class PageDeserializer(Deserializer[Page]):
    def deserialize(self, serialized_page: str) -> Page:
        return Page(url=None, content=serialized_page)


class PageRepository(Repository[Page], ABC):
    pass


class FilePageRepository(PageRepository):
    def __init__(self):
        self._serializer = PageSerializer()
        self._deserializer = PageDeserializer()
        makedirs(PAGES_DIR, exist_ok=True)

    def load(self, url: str) -> Optional[Page]:
        file_path = url_to_file_path(url)
        return self._load_file(file_path)

    def load_all(self) -> List[Page]:
        pages = list[Page]()
        for file_name in listdir(PAGES_DIR):
            file_path = self._get_file_path(file_name)
            page = self._load_file(file_path)
            if page is None:
                continue
            pages.append(page)
        return pages

    def save(self, page: Page) -> Page:
        file_path = url_to_file_path(page.url)
        self._save_file(file_path, page)
        return page

    def _get_file_path(self, file_name: str) -> str:
        return join(PAGES_DIR, file_name)

    def _load_file(self, file_path: str) -> Optional[Page]:
        print(f'Loading file {file_path}')
        if not isfile(file_path):
            return None
        with open(file_path, 'r', encoding='utf-8') as file:
            page = self._deserializer.deserialize(file.read())
            url = file_path_to_url(file_path)
            page.url = url
            return page

    def _save_file(self, file_path: str, page: Page) -> None:
        print(f'Saving file {file_path}')
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(self._serializer.serialize(page))
