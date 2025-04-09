from abc import ABC, abstractmethod


class QueryPlanNode(ABC):
    @abstractmethod
    def accept(self, visitor, *args, **kwargs):
        return NotImplemented


class SequentialScanQueryPlanNode(QueryPlanNode):
    def accept(self, visitor, *args, **kwargs):
        return visitor.visit_sequential_scan(self, *args, **kwargs)


class IndexScanQueryPlanNode(QueryPlanNode):
    def __init__(self, value: str):
        self.value = value

    def accept(self, visitor, *args, **kwargs):
        return visitor.visit_index_scan(self, *args, **kwargs)


class IntersectQueryPlanNode(QueryPlanNode):
    def __init__(self, lhs: QueryPlanNode, rhs: QueryPlanNode):
        self.lhs = lhs
        self.rhs = rhs

    def accept(self, visitor, *args, **kwargs):
        return visitor.visit_intersect(self, *args, **kwargs)


class UnionQueryPlanNode(QueryPlanNode):
    def __init__(self, lhs: QueryPlanNode, rhs: QueryPlanNode):
        self.lhs = lhs
        self.rhs = rhs

    def accept(self, visitor, *args, **kwargs):
        return visitor.visit_union(self, *args, **kwargs)


class DifferenceQueryPlanNode(QueryPlanNode):
    def __init__(self, lhs: QueryPlanNode, rhs: QueryPlanNode):
        self.lhs = lhs
        self.rhs = rhs

    def accept(self, visitor, *args, **kwargs):
        return visitor.visit_difference(self, *args, **kwargs)


class NoopQueryPlanNode(QueryPlanNode):
    def accept(self, visitor, *args, **kwargs):
        return visitor.visit_noop(self, *args, **kwargs)


class QueryPlanNodeVisitor(ABC):
    @abstractmethod
    def visit_sequential_scan(self, node: SequentialScanQueryPlanNode, *args, **kwargs):
        return NotImplemented

    @abstractmethod
    def visit_index_scan(self, node: IndexScanQueryPlanNode, *args, **kwargs):
        return NotImplemented

    @abstractmethod
    def visit_intersect(self, node: IntersectQueryPlanNode, *args, **kwargs):
        return NotImplemented

    @abstractmethod
    def visit_union(self, node: UnionQueryPlanNode, *args, **kwargs):
        return NotImplemented

    @abstractmethod
    def visit_difference(self, node: DifferenceQueryPlanNode, *args, **kwargs):
        return NotImplemented

    @abstractmethod
    def visit_noop(self, node: NoopQueryPlanNode, *args, **kwargs):
        return NotImplemented
