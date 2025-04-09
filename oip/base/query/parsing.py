from abc import ABC, abstractmethod
from typing import List

from oip.base.query.node import QueryNode
from oip.base.query.token import QueryToken


class QueryParser(ABC):
    @abstractmethod
    def parse_query_tokens(self, query_tokens: List[QueryToken]) -> QueryNode:
        return NotImplemented
