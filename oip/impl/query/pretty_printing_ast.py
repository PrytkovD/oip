from oip.base.query.node import NotQueryNode, OrQueryNode, AndQueryNode, WordQueryNode, QueryNodeVisitor, EmptyQueryNode


class PrettyPrintQueryNodeVisitor(QueryNodeVisitor):
    def __init__(self):
        self._indent = " " * 2

    def visit_word(self, node: WordQueryNode, indent: int = 0) -> str:
        return self._indent * indent + f"WORD({node.value})"

    def visit_and(self, node: AndQueryNode, indent: int = 0) -> str:
        lines = [
            self._indent * indent + "AND(",
            node.lhs.accept(self, indent + 1),
            node.rhs.accept(self, indent + 1),
            self._indent * indent + ")"
        ]
        return "\n".join(lines)

    def visit_or(self, node: OrQueryNode, indent: int = 0) -> str:
        lines = [
            self._indent * indent + "OR(",
            node.lhs.accept(self, indent + 1),
            node.rhs.accept(self, indent + 1),
            self._indent * indent + ")"
        ]
        return "\n".join(lines)

    def visit_not(self, node: NotQueryNode, indent: int = 0) -> str:
        lines = [
            self._indent * indent + "NOT(",
            node.child.accept(self, indent + 1),
            self._indent * indent + ")"
        ]
        return "\n".join(lines)

    def visit_empty(self, node: EmptyQueryNode, indent: int = 0):
        return self._indent * indent + f"EMPTY"


PRETTY_PRINT_QUERY_NODE_VISITOR = PrettyPrintQueryNodeVisitor()


def pretty_print_query_node_visitor() -> PrettyPrintQueryNodeVisitor:
    return PRETTY_PRINT_QUERY_NODE_VISITOR
