from database.table import create_table
from oip.impl.util.util import PAGES_DIR, TOKENS_DIR, LEMMAS_DIR

PAGE = create_table(
    'page',
    'id', 'url',
    storage_dir=PAGES_DIR,
    cache_size=100
)

PAGE_CONTENT = create_table(
    'page_content',
    'page_id', 'content',
    storage_dir=PAGES_DIR,
    page_size=1,
    cache_size=100
)

PAGE_TOKENS = create_table(
    'page_tokens',
    'page_url', 'token',
    storage_dir=TOKENS_DIR,
    cache_size=100
)

PAGE_LEMMAS = create_table(
    'page_lemmas',
    'id', 'page_url', 'lemma',
    storage_dir=LEMMAS_DIR,
    cache_size=100
)

LEMMAS_TOKENS = create_table(
    'lemmas_tokens',
    'lemma_id', 'token',
    storage_dir=LEMMAS_DIR,
    cache_size=100
)
