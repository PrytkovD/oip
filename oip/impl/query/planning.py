from oip.base.query.node import *
from oip.base.query.plan_node import *
from oip.base.query.planning import QueryPlanner


class PlanningQueryNodeVisitor(QueryNodeVisitor):
    def visit_word(self, node: WordQueryNode) -> QueryPlanNode:
        return IndexScanQueryPlanNode(node.value)

    def visit_and(self, node: AndQueryNode) -> QueryPlanNode:
        lhs_is_not = isinstance(node.lhs, NotQueryNode)
        rhs_is_not = isinstance(node.rhs, NotQueryNode)

        if lhs_is_not == rhs_is_not:
            return IntersectQueryPlanNode(node.lhs.accept(self), node.rhs.accept(self))
        if lhs_is_not:
            return DifferenceQueryPlanNode(node.rhs.accept(self), node.lhs.child.accept(self))
        if rhs_is_not:
            return DifferenceQueryPlanNode(node.lhs.accept(self), node.rhs.child.accept(self))

    def visit_or(self, node: OrQueryNode) -> QueryPlanNode:
        return UnionQueryPlanNode(node.lhs.accept(self), node.rhs.accept(self))

    def visit_not(self, node: NotQueryNode) -> QueryPlanNode:
        return DifferenceQueryPlanNode(SequentialScanQueryPlanNode(), node.child.accept(self))

    def visit_empty(self, node: EmptyQueryNode):
        return NoopQueryPlanNode()


class SimpleQueryPlanner(QueryPlanner):
    def __init__(self):
        self._planning_visitor = PlanningQueryNodeVisitor()

    def plan_query_execution(self, query_node: QueryNode) -> QueryPlanNode:
        plan_node = query_node.accept(self._planning_visitor)
        return plan_node


DEFAULT_QUERY_PLANNER = SimpleQueryPlanner()


def default_query_planner() -> QueryPlanner:
    return DEFAULT_QUERY_PLANNER
