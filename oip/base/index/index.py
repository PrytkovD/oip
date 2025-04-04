class IndexEntry:
    def __init__(self, page_file_path: str, page_url: str):
        self.page_file_path = page_file_path
        self.page_url = page_url

    def __eq__(self, other):
        return self.page_file_path == other.page_file_path

    def __hash__(self):
        return hash(self.page_file_path)

    def __lt__(self, other) -> bool:
        return self.page_file_path < other.page_file_path
