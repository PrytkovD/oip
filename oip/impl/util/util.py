import hashlib
import os
import os.path
from urllib import parse

OUT_DIR = "out"
PAGES_DIR = os.path.join(OUT_DIR, "pages")
TOKENS_DIR = os.path.join(OUT_DIR, "tokens")
LEMMAS_DIR = os.path.join(OUT_DIR, "lemmas")
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


def progress(iterable, description='', max_value=None):
    max_width = 80
    terminal_width = os.get_terminal_size().columns

    width = min(terminal_width, max_width)

    description_width = 0
    if description:
        description_width = len(description) + 8 - len(description) % 8 + 1
    progress_width = 4 + 1

    progress_bar_width = width - description_width - progress_width - 2

    filled_symbol = '█'
    unfilled_symbol = ' '

    if max_value is None:
        max_value = len(iterable)

    try:
        for index, value in enumerate(iterable):
            progress_percent = min(int((index + 1) / max_value * 100), 100)
            filled_width = int(progress_percent * progress_bar_width / 100)
            unfilled_width = progress_bar_width - filled_width
            print(
                f"{description:<{description_width}}|{filled_symbol * filled_width}{unfilled_symbol * unfilled_width}| {progress_percent}%",
                end="\r")
            yield value

        if description:
            print(f"{description:<{description_width}}{' ':<{width - description_width}}")
        else:
            print(" " * width, end="\r")
    except GeneratorExit:
        if description:
            print(f"{description:<{description_width}}{' ':<{width - description_width}}")
        else:
            print(" " * width, end="\r")
