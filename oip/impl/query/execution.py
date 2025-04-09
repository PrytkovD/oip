from typing import List

from oip.base.page_index.page_index import PageIndex
from oip.base.query.execution import QueryPlanExecutor
from oip.base.query.node import QueryNode
from oip.base.query.plan_node import QueryPlanNodeVisitor, NoopQueryPlanNode, DifferenceQueryPlanNode, \
    UnionQueryPlanNode, IntersectQueryPlanNode, IndexScanQueryPlanNode, SequentialScanQueryPlanNode
from oip.base.token.token import Token
from oip.base.token_index.token_index import TokenIndex
from oip.impl.page_index.page_index import default_page_index
from oip.impl.token_index.token_index import default_token_index


class ExecutorVisitor(QueryPlanNodeVisitor):
    def __init__(self, token_index: TokenIndex, page_index: PageIndex):
        self._token_index = token_index
        self._page_index = page_index

    def visit_sequential_scan(self, node: SequentialScanQueryPlanNode):
        return set(self._page_index.get_all_page_urls())

    def visit_index_scan(self, node: IndexScanQueryPlanNode):
        return set(self._token_index.get_page_urls_by_token(Token(node.value)))

    def visit_intersect(self, node: IntersectQueryPlanNode):
        return node.lhs.accept(self).intersection(node.rhs.accept(self))

    def visit_union(self, node: UnionQueryPlanNode):
        return node.lhs.accept(self).union(node.rhs.accept(self))

    def visit_difference(self, node: DifferenceQueryPlanNode):
        return node.lhs.accept(self).difference(node.rhs.accept(self))

    def visit_noop(self, node: NoopQueryPlanNode):
        return set()


class SimpleQueryPlanExecutor(QueryPlanExecutor):
    def __init__(self, token_index: TokenIndex, page_index: PageIndex):
        self._visitor = ExecutorVisitor(token_index, page_index)

    def execute_query_plan(self, query_plan_node: QueryNode) -> List[str]:
        return list(query_plan_node.accept(self._visitor))


DEFAULT_QUERY_EXECUTOR = SimpleQueryPlanExecutor(
    token_index=default_token_index(),
    page_index=default_page_index()
)


def default_query_executor() -> QueryPlanExecutor:
    return DEFAULT_QUERY_EXECUTOR
