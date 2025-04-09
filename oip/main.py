from typing import List, Optional

from oip.base.query.query import Query
from oip.impl.lemma.lemmatization import default_lemmatizer
from oip.impl.lemma.repository import default_page_lemmas_repository
from oip.impl.page.downloading import default_page_downloader
from oip.impl.page.repository import default_page_repository
from oip.impl.query.execution import default_query_executor
from oip.impl.query.parsing import default_query_parser
from oip.impl.query.planning import default_query_planner
from oip.impl.query.pretty_printing_ast import pretty_print_query_node_visitor
from oip.impl.query.pretty_printing_plan import pretty_print_query_plan_node_visitor
from oip.impl.query.simplification import SimplifyingQueryNodeVisitor
from oip.impl.query.tokenization import default_query_tokenizer
from oip.impl.token.repository import default_page_tokens_repository
from oip.impl.token.tokenization import default_tokenizer
from oip.impl.token_index.token_index import default_token_index
from oip.impl.util.util import progress


def get_urls() -> List[str]:
    return [f'https://www.rfc-editor.org/rfc/rfc{x}.html' for x in range(1, 1001)]


def crawl_pages(urls: List[str], max_urls_to_crawl: Optional[int] = None):
    page_downloader = default_page_downloader()

    page_repository = default_page_repository()

    crawled_urls = 0
    max_urls_to_crawl = min(max_urls_to_crawl, len(urls))
    for url in progress(urls, description="Crawling pages...", max_value=max_urls_to_crawl):
        if crawled_urls >= max_urls_to_crawl:
            break
        page = page_downloader.download(url)
        if not page:
            continue
        page_repository.save(page)
        crawled_urls += 1


def tokenize_pages():
    tokenizer = default_tokenizer()

    page_repository = default_page_repository()
    page_tokens_repository = default_page_tokens_repository()

    all_pages = page_repository.load_all()
    for page in progress(all_pages, description="Tokenizing pages..."):
        page_tokens = tokenizer.tokenize(page)
        page_tokens_repository.save(page_tokens)


def lemmatize_tokens():
    lemmatizer = default_lemmatizer()

    page_tokens_repository = default_page_tokens_repository()
    page_lemmas_repository = default_page_lemmas_repository()

    all_page_tokens = page_tokens_repository.load_all()
    for page_tokens in progress(all_page_tokens, description="Lemmatizing tokens..."):
        page_lemmas = lemmatizer.lemmatize(page_tokens)
        page_lemmas_repository.save(page_lemmas)


def build_token_index():
    inverted_index = default_token_index()

    page_lemmas_repository = default_page_lemmas_repository()

    all_page_lemmas = page_lemmas_repository.load_all()
    for page_lemmas in progress(all_page_lemmas, description="Building token index..."):
        for lemma in page_lemmas.lemmas:
            inverted_index.add_entry(token=lemma.lemma, page_url=page_lemmas.page_url)


def repl():
    tokenizer = default_query_tokenizer()
    parser = default_query_parser()
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
        "  a! <query> | Pretty print AST",
        "  s! <query> | Pretty print simplified AST",
        "  p! <query> | Pretty print query plan"
    ])

    print(f"Entering REPL mode...")
    print(help_str)

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

        ast = ast.accept(SimplifyingQueryNodeVisitor())

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
