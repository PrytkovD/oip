from typing import Optional


class QueryToken:
    def __init__(self, type: str, value: Optional[str] = None):
        self.type = type
        self.value = value
