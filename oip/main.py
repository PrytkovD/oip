import atexit
import shutil
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import List, Optional

from oip.base.page.page import Page
from oip.base.query.query import Query
from oip.impl.lemma.lemmatization import default_lemmatizer
from oip.impl.lemma.repository import default_page_lemmas_repository, PageLemmasMultiFileRepository
from oip.impl.page.downloading import default_page_downloader
from oip.impl.page.repository import default_page_repository, PageMultiFileRepository
from oip.impl.page_index.page_index import default_page_index
from oip.impl.query.execution import default_query_executor
from oip.impl.query.parsing import default_query_parser
from oip.impl.query.planning import default_query_planner
from oip.impl.query.pretty_printing_ast import pretty_print_query_node_visitor
from oip.impl.query.pretty_printing_plan import pretty_print_query_plan_node_visitor
from oip.impl.query.simplification import default_query_simplifier
from oip.impl.query.tokenization import default_query_tokenizer
from oip.impl.tf_idf.repository import PageTokensTfIdfsMultiFileRepository, \
    default_page_tokens_tf_idfs_repository, default_page_lemmas_tf_idfs_repository, PageLemmasTfIdfsMultiFileRepository
from oip.impl.token.repository import default_page_tokens_repository, PageTokensMultiFileRepository
from oip.impl.token.tokenization import default_tokenizer
from oip.impl.token_index.token_index import default_token_index
from oip.impl.util.progress import progress
from oip.impl.util.tables import *
from oip.impl.util.util import OUT_DIR, TF_IDF_DIR


def get_urls() -> List[str]:
    return [f'https://www.rfc-editor.org/rfc/rfc{x}.html' for x in range(1, 1001)]


def crawl_pages(urls: List[str], max_urls_to_crawl: Optional[int] = None):
    page_downloader = default_page_downloader()

    page_repository = default_page_repository()

    pages = list[Page]()
    max_urls_to_crawl = min(max_urls_to_crawl, len(urls))
    crawled_urls = 0

    with progress(description='Crawling pages...', max_value=max_urls_to_crawl) as progress_bar:
        with ThreadPoolExecutor() as executor:
            future_to_url = {executor.submit(page_downloader.download, url): url for url in urls[:max_urls_to_crawl]}
            for future in as_completed(future_to_url):
                page = future.result()
                if not page:
                    continue
                pages.append(page)
                progress_bar.increment()
                crawled_urls += 1

        for url in urls[max_urls_to_crawl:]:
            if crawled_urls >= max_urls_to_crawl:
                break
            page = page_downloader.download(url)
            if not page:
                continue
            pages.append(page)
            progress_bar.increment()
            crawled_urls += 1

    for page in pages:
        page_repository.save(page)

    page_repository.load_all_into(
        PageMultiFileRepository(
            dir_path=PAGES_DIR,
            index=default_page_index()
        )
    )


def tokenize_pages():
    tokenizer = default_tokenizer()

    page_repository = default_page_repository()
    page_tokens_repository = default_page_tokens_repository()

    all_pages = page_repository.load_all()
    for page in progress(all_pages, description="Tokenizing pages..."):
        page_tokens = tokenizer.tokenize(page)
        page_tokens_repository.save(page_tokens)

    page_tokens_repository.load_all_into(
        PageTokensMultiFileRepository(dir_path=TOKENS_DIR)
    )


def lemmatize_tokens():
    lemmatizer = default_lemmatizer()

    page_tokens_repository = default_page_tokens_repository()
    page_lemmas_repository = default_page_lemmas_repository()

    all_page_tokens = page_tokens_repository.load_all()
    for page_tokens in progress(all_page_tokens, description="Lemmatizing tokens..."):
        page_lemmas = lemmatizer.lemmatize(page_tokens)
        page_lemmas_repository.save(page_lemmas)

    page_lemmas_repository.load_all_into(
        PageLemmasMultiFileRepository(dir_path=LEMMAS_DIR)
    )


def build_token_index():
    inverted_index = default_token_index()

    page_lemmas_repository = default_page_lemmas_repository()

    all_page_lemmas = page_lemmas_repository.load_all()
    for page_lemmas in progress(all_page_lemmas, description="Building token index..."):
        for lemma in page_lemmas.lemmas:
            inverted_index.add_entry(token=lemma.lemma, page_url=page_lemmas.page_url)


def compute_tf_idf():
    print('Computing TF-IDF...')

    page_tokens_tf_idf_repository = default_page_tokens_tf_idfs_repository()

    page_tokens_tf_idf_repository.load_all_into(
        PageTokensTfIdfsMultiFileRepository(dir_path=TF_IDF_DIR)
    )

    page_lemmas_tf_idf_repository = default_page_lemmas_tf_idfs_repository()

    page_lemmas_tf_idf_repository.load_all_into(
        PageLemmasTfIdfsMultiFileRepository(dir_path=TF_IDF_DIR)
    )


def repl():
    tokenizer = default_query_tokenizer()
    parser = default_query_parser()
    simplifier = default_query_simplifier()
    planner = default_query_planner()
    executor = default_query_executor()

    ast_pretty_print_visitor = pretty_print_query_node_visitor()
    plan_pretty_print_visitor = pretty_print_query_plan_node_visitor()

    help_str = "\n".join([
        "Usage:",
        "  <query>    | Execute query",
        "  ?          | Print this message",
        "  q          | Quit REPL",
        "  c!         | Crawl",
        "  d!         | Toggle 'delete crawled data on exit' hook",
        "  a! <query> | Pretty print AST",
        "  s! <query> | Pretty print simplified AST",
        "  p! <query> | Pretty print query plan"
    ])

    print(f"Entering REPL mode...")
    print(help_str)

    delete_data = False

    while True:
        pretty_print_ast = False
        pretty_print_simple_ast = False
        pretty_print_plan = False
        raw_input = input("> ")

        if not raw_input:
            continue

        if raw_input[0] == "q":
            break
        elif raw_input[0] == "?":
            print(help_str)
            continue
        elif len(raw_input) > 1 and raw_input[1] == "!":
            if raw_input[0] == "c":
                crawl_pages(get_urls(), max_urls_to_crawl=100)
                tokenize_pages()
                lemmatize_tokens()
                build_token_index()
                compute_tf_idf()
                continue
            elif raw_input[0] == "d":
                def get_atexit(delete: bool, f, *args, **kwargs):
                    if delete:
                        return atexit.unregister(f)
                    else:
                        return atexit.register(f, *args, **kwargs)

                delete_data = not delete_data
                print(f'{'Will' if delete_data else "Won't"} delete crawled data on exit')
                get_atexit(delete_data, PAGE.dump)
                get_atexit(delete_data, PAGE_CONTENT.dump)
                get_atexit(delete_data, PAGE_TOKENS.dump)
                get_atexit(delete_data, PAGE_LEMMAS.dump)
                get_atexit(delete_data, LEMMAS_TOKENS.dump)
                get_atexit(not delete_data, shutil.rmtree, OUT_DIR)

                continue
            elif raw_input[0] == "a":
                pretty_print_ast = True
                raw_input = raw_input[2:]
            elif raw_input[0] == "s":
                pretty_print_simple_ast = True
                raw_input = raw_input[2:]
            elif raw_input[0] == "p":
                pretty_print_plan = True
                raw_input = raw_input[2:]
            else:
                print("Unrecognized command. Use '?' to see available commands")
                continue

        query = Query(raw_input)
        if not query:
            continue

        tokens = tokenizer.tokenize_query(query)
        if not tokens:
            continue

        ast = parser.parse_query_tokens(tokens)
        if not ast:
            continue

        if pretty_print_ast:
            print(ast.accept(ast_pretty_print_visitor))
            continue

        ast = simplifier.simplify_query(ast)

        if pretty_print_simple_ast:
            print(ast.accept(ast_pretty_print_visitor))
            continue

        plan = planner.plan_query_execution(ast)
        if not plan:
            continue

        if pretty_print_plan:
            print(plan.accept(plan_pretty_print_visitor))
            continue

        urls = executor.execute_query_plan(plan)
        if urls:
            print("\n".join(urls))
        print(f"Query returned {len(urls)} URLs")


def main():
    repl()


if __name__ == "__main__":
    main()
