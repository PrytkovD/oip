from abc import ABC, abstractmethod
from typing import List

from oip.base.query.query import Query
from oip.base.query.token import QueryToken


class QueryTokenizer(ABC):
    @abstractmethod
    def tokenize_query(self, query: Query) -> List[QueryToken]:
        return NotImplemented
