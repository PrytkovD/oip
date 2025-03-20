from os import path
from urllib.parse import quote_plus, unquote_plus

PAGES_DIR = 'pages'
INDEX_FILE = 'index.txt'


def url_to_file_path(url: str) -> str:
    file_name = quote_plus(url)
    return path.join(PAGES_DIR, file_name)


def file_path_to_url(file_path: str) -> str:
    file_name = path.basename(file_path)
    return unquote_plus(file_name)
