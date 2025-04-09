from abc import ABC, abstractmethod
from typing import List

from oip.base.query.plan_node import QueryPlanNode


class QueryPlanExecutor(ABC):
    @abstractmethod
    def execute_query_plan(self, query_plan_node: QueryPlanNode) -> List[str]:
        return NotImplemented
