import os.path
from urllib import parse

OUT_DIR = "out"
PAGES_DIR = os.path.join(OUT_DIR, "pages")
TOKENS_DIR = os.path.join(OUT_DIR, "tokens")
LEMMAS_DIR = os.path.join(OUT_DIR, "lemmas")
INDEX_FILE = os.path.join(OUT_DIR, "index.txt")


def quote(unquoted_str: str) -> str:
    return parse.quote(unquoted_str, safe='')


def unquote(quoted_str: str) -> str:
    return parse.unquote(quoted_str)
