from database.column import Column
from database.table import create_table
from oip.impl.util.util import PAGES_DIR, TOKENS_DIR, LEMMAS_DIR, TF_IDF_DIR

PAGE = create_table(
    'page',
    Column('id', str), Column('url', str),
    storage_dir=PAGES_DIR,
    cache_size=100
)

PAGE_CONTENT = create_table(
    'page_content',
    Column('page_id', str), Column('content', str),
    storage_dir=PAGES_DIR,
    page_size=1,
    cache_size=100
)

PAGE_TOKENS = create_table(
    'page_tokens',
    Column('page_url', str), Column('token', str),
    storage_dir=TOKENS_DIR,
    cache_size=100
)

PAGE_LEMMAS = create_table(
    'page_lemmas',
    Column('id', str), Column('page_url', str), Column('lemma', str),
    storage_dir=LEMMAS_DIR,
    cache_size=100
)

LEMMAS_TOKENS = create_table(
    'lemmas_tokens',
    Column('lemma_id', str), Column('token', str),
    storage_dir=LEMMAS_DIR,
    cache_size=100
)

PAGE_TOKENS_TF_IDFS = create_table(
    'page_tokens_tf_idfs',
    Column('page_url', str), Column('token', str), Column('idf', float), Column('tf_idf', float),
    storage_dir=TF_IDF_DIR,
    cache_size=100
)

PAGE_LEMMAS_TF_IDFS = create_table(
    'page_lemmas_tf_idfs',
    Column('page_url', str), Column('lemma', str), Column('idf', float), Column('tf_idf', float),
    storage_dir=TF_IDF_DIR,
    cache_size=100
)

LEMMAS = create_table(
    'lemmas',
    Column('lemma', str),
    storage_dir=LEMMAS_DIR,
    cache_size=100
)

PAGE_LEMMA_MATRIX = create_table(
    'page_lemmma_matrix',
    Column('page_url', str), Column('vector', list[float]),
    storage_dir=TF_IDF_DIR,
    cache_size=100
)
