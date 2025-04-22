from abc import ABC, abstractmethod

from oip.base.query.node import QueryNode


class QuerySimplifier(ABC):
    @abstractmethod
    def simplify_query(self, query_node: QueryNode) -> QueryNode:
        return NotImplemented
