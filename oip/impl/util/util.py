import hashlib
import os.path
from urllib import parse

OUT_DIR = "out"
PAGES_DIR = os.path.join(OUT_DIR, "pages")
TOKENS_DIR = os.path.join(OUT_DIR, "tokens")
LEMMAS_DIR = os.path.join(OUT_DIR, "lemmas")
TF_IDF_DIR = os.path.join(OUT_DIR, "tf_idf")
PAGE_INDEX_FILE = os.path.join(OUT_DIR, "index.txt")
TOKEN_INDEX_FILE = os.path.join(OUT_DIR, "token_index.txt")


def quote(unquoted_str: str) -> str:
    return parse.quote(unquoted_str, safe='')


def unquote(quoted_str: str) -> str:
    return parse.unquote(quoted_str)


def clean(dirty_str: str) -> str:
    return dirty_str.encode("ascii", "ignore").decode("ascii")


def next_prime(n: int) -> int:
    if n <= 0:
        return 1

    if n == 1:
        return 2

    num = n + 1
    while True:
        is_prime = True

        div = 2
        while div * div <= num:
            if num % div == 0:
                is_prime = False
                break
            div += 1

        if is_prime:
            return num

        num += 1


def stable_hash(obj: str) -> int:
    tuple_bytes = obj.encode('utf-8')
    md5 = hashlib.md5(tuple_bytes)
    return int(md5.hexdigest(), 16)


