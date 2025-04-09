from oip.base.query.plan_node import QueryPlanNodeVisitor, DifferenceQueryPlanNode, UnionQueryPlanNode, \
    IntersectQueryPlanNode, IndexScanQueryPlanNode, NoopQueryPlanNode, SequentialScanQueryPlanNode


class PrettyPrintQueryPlanNodeVisitor(QueryPlanNodeVisitor):
    def __init__(self):
        self._indent = " " * 2

    def visit_sequential_scan(self, node: SequentialScanQueryPlanNode, indent: int = 0) -> str:
        return self._indent * indent + f"Sequential scan"

    def visit_index_scan(self, node: IndexScanQueryPlanNode, indent: int = 0) -> str:
        return self._indent * indent + f"Index scan for '{node.value}'"

    def visit_intersect(self, node: IntersectQueryPlanNode, indent: int = 0) -> str:
        lines = [
            self._indent * indent + "Intersection(",
            node.lhs.accept(self, indent + 1) + ',',
            node.rhs.accept(self, indent + 1),
            self._indent * indent + ")",
        ]
        return "\n".join(lines)

    def visit_union(self, node: UnionQueryPlanNode, indent: int = 0) -> str:
        lines = [
            self._indent * indent + "Union(",
            node.lhs.accept(self, indent + 1) + ',',
            node.rhs.accept(self, indent + 1),
            self._indent * indent + ")",
        ]
        return "\n".join(lines)

    def visit_difference(self, node: DifferenceQueryPlanNode, indent: int = 0) -> str:
        lines = [
            self._indent * indent + "Difference(",
            node.lhs.accept(self, indent + 1) + ',',
            node.rhs.accept(self, indent + 1),
            self._indent * indent + ")",
        ]
        return "\n".join(lines)

    def visit_noop(self, node: NoopQueryPlanNode, indent: int = 0):
        return self._indent * indent + f"Noop"


PRETTY_PRINT_QUERY_PLAN_NODE_VISITOR = PrettyPrintQueryPlanNodeVisitor()


def pretty_print_query_plan_node_visitor() -> PrettyPrintQueryPlanNodeVisitor:
    return PRETTY_PRINT_QUERY_PLAN_NODE_VISITOR
