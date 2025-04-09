from abc import ABC, abstractmethod


class QueryNode(ABC):
    @abstractmethod
    def accept(self, visitor, *args, **kwargs):
        return NotImplemented


class WordQueryNode(QueryNode):
    def __init__(self, value: str):
        self.value = value

    def accept(self, visitor, *args, **kwargs):
        return visitor.visit_word(self, *args, **kwargs)

    def __eq__(self, other):
        return isinstance(other, WordQueryNode) and self.value == other.value

    def __hash__(self):
        return hash(str(self))

    def __repr__(self):
        return f"{self.value}"


class AndQueryNode(QueryNode):
    def __init__(self, lhs: QueryNode, rhs: QueryNode):
        self.lhs = lhs
        self.rhs = rhs

    def accept(self, visitor, *args, **kwargs):
        return visitor.visit_and(self, *args, **kwargs)

    def __eq__(self, other):
        return (isinstance(other, AndQueryNode) and
                ((self.lhs == other.lhs and self.rhs == other.rhs) or
                 (self.lhs == other.rhs and self.rhs == other.lhs)))

    def __hash__(self):
        return hash(str(self))

    def __repr__(self):
        return f"({self.lhs} AND {self.rhs})"


class OrQueryNode(QueryNode):
    def __init__(self, lhs: QueryNode, rhs: QueryNode):
        self.lhs = lhs
        self.rhs = rhs

    def accept(self, visitor, *args, **kwargs):
        return visitor.visit_or(self, *args, **kwargs)

    def __eq__(self, other):
        return (isinstance(other, OrQueryNode) and
                ((self.lhs == other.lhs and self.rhs == other.rhs) or
                 (self.lhs == other.rhs and self.rhs == other.lhs)))

    def __hash__(self):
        return hash(str(self))

    def __repr__(self):
        return f"({self.lhs} OR {self.rhs})"


class NotQueryNode(QueryNode):
    def __init__(self, child: QueryNode):
        self.child = child

    def accept(self, visitor, *args, **kwargs):
        return visitor.visit_not(self, *args, **kwargs)

    def __eq__(self, other):
        return isinstance(other, NotQueryNode) and self.child == other.child

    def __hash__(self):
        return hash(str(self))

    def __repr__(self):
        return f"NOT {self.child}"


class EmptyQueryNode(QueryNode):
    def accept(self, visitor, *args, **kwargs):
        return visitor.visit_empty(self, *args, **kwargs)

    def __eq__(self, other):
        return isinstance(other, EmptyQueryNode)

    def __hash__(self):
        return hash(str(self))

    def __repr__(self):
        return f"EMPTY"


class QueryNodeVisitor(ABC):
    @abstractmethod
    def visit_word(self, node: WordQueryNode, *args, **kwargs):
        return NotImplemented

    @abstractmethod
    def visit_and(self, node: AndQueryNode, *args, **kwargs):
        return NotImplemented

    @abstractmethod
    def visit_or(self, node: OrQueryNode, *args, **kwargs):
        return NotImplemented

    @abstractmethod
    def visit_not(self, node: NotQueryNode, *args, **kwargs):
        return NotImplemented

    @abstractmethod
    def visit_empty(self, node: EmptyQueryNode, *args, **kwargs):
        return NotImplemented
