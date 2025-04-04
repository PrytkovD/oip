class Page:
    def __init__(self, url: str, content: str):
        self.url = url
        self.content = content

    def __eq__(self, other):
        return self.url == other.url

    def __hash__(self):
        return hash(self.url)
