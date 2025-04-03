from bs4 import BeautifulSoup

from oip.base.page.page import Page
from oip.base.token.text_extraction import TextExtractor


class BeautifulSoupTextExtractor(TextExtractor):
    def extract(self, page: Page) -> str:
        soup = BeautifulSoup(page.content, "html.parser")
        for not_wanted in soup(["script", "style", "noscript", "head"]):
            not_wanted.decompose()
        text = soup.get_text(separator="\n", strip=True)
        clean_lines = [line.strip().encode('ascii', 'ignore').decode('ascii') for line in text.splitlines() if line.strip()]
        return '\n'.join(clean_lines)


DEFAULT_TEXT_EXTRACTOR = BeautifulSoupTextExtractor()


def default_text_extractor() -> TextExtractor:
    return DEFAULT_TEXT_EXTRACTOR
