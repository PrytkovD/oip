from abc import ABC, abstractmethod

from oip.base.query.node import QueryNode
from oip.base.query.plan_node import QueryPlanNode


class QueryPlanner(ABC):
    @abstractmethod
    def plan_query_execution(self, query_node: QueryNode) -> QueryPlanNode:
        return NotImplemented