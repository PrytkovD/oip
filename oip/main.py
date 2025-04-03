from typing import List

from oip.impl.lemma.lemmatization import default_lemmatizer
from oip.impl.lemma.repository import default_page_lemmas_repository
from oip.impl.page.crawling import default_crawler
from oip.impl.page.repository import default_page_repository
from oip.impl.token.repository import default_page_tokens_repository
from oip.impl.token.tokenization import default_tokenizer


def get_urls() -> List[str]:
    return [f'https://www.rfc-editor.org/rfc/rfc{x}.html' for x in range(1, 1001)]


def main():
    crawler = default_crawler()
    tokenizer = default_tokenizer()
    lemmatizer = default_lemmatizer()

    page_repository = default_page_repository()
    page_tokens_repository = default_page_tokens_repository()
    page_lemmas_repository = default_page_lemmas_repository()

    urls = get_urls()
    crawled_urls = 0
    max_crawled_urls = 100

    for url in urls:
        print(f'Crawling page {url}')
        pages = crawler.crawl([url], max_pages=1)

        if not pages:
            print(f'\tFailed crawl page')
            continue

        page = pages[0]

        print(f'\tTokenizing...')
        page_tokens = tokenizer.tokenize(page)

        print(f'\tLemmatizing tokens...')
        page_lemmas = lemmatizer.lemmatize(page_tokens)

        try:
            print(f'\tSaving page content...')
            page_repository.save(page)

            print(f'\tSaving tokens...')
            page_tokens_repository.save(page_tokens)

            print(f'\tSaving lemmas...')
            page_lemmas_repository.save(page_lemmas)
        except Exception as e:
            print(f'\tFailed to save')
            continue

        crawled_urls += 1

        print(f'Crawled {crawled_urls}/{max_crawled_urls} URLs')

        if crawled_urls >= 100:
            break


if __name__ == "__main__":
    main()
