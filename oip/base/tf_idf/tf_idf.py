from typing import List


class TfIdf:
    def __init__(self, token: str, idf: float, tf_idf: float):
        self.token = token
        self.idf = idf
        self.tf_idf = tf_idf

    def __eq__(self, other):
        return self.token == other.token

    def __lt__(self, other) -> bool:
        return self.token < other.token

    def __hash__(self):
        return hash(self.token)


class PageTfIdfs:
    def __init__(self, page_url: str, tf_idfs: List[TfIdf]):
        self.page_url = page_url
        self.tf_idfs = tf_idfs

    def __eq__(self, other):
        return self.page_url == other.page_url

    def __hash__(self):
        return hash(self.page_url)
