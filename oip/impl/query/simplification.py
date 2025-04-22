import random

from oip.base.query.node import QueryNodeVisitor, WordQueryNode, QueryNode, AndQueryNode, OrQueryNode, NotQueryNode, \
    EmptyQueryNode
from oip.base.query.simplification import QuerySimplifier
from oip.impl.util.util import progress


class SimplificationRule(QueryNodeVisitor):
    def visit_word(self, node: WordQueryNode) -> QueryNode:
        return node

    def visit_and(self, node: AndQueryNode) -> QueryNode:
        return node

    def visit_or(self, node: OrQueryNode) -> QueryNode:
        return node

    def visit_not(self, node: NotQueryNode) -> QueryNode:
        return node

    def visit_empty(self, node: EmptyQueryNode) -> QueryNode:
        return node


class IdentityLaw(SimplificationRule):
    def visit_or(self, node: OrQueryNode) -> QueryNode:
        lhs = node.lhs.accept(self)
        rhs = node.rhs.accept(self)

        lhs_is_empty = isinstance(lhs, EmptyQueryNode)
        rhs_is_empty = isinstance(rhs, EmptyQueryNode)

        # 0 + A = A
        # A + 0 = A
        if lhs_is_empty:
            return rhs
        if rhs_is_empty:
            return lhs

        return OrQueryNode(lhs, rhs)


class DominationLaw(SimplificationRule):
    def visit_and(self, node: AndQueryNode) -> QueryNode:
        lhs = node.lhs.accept(self)
        rhs = node.rhs.accept(self)

        lhs_is_empty = isinstance(lhs, EmptyQueryNode)
        rhs_is_empty = isinstance(rhs, EmptyQueryNode)

        # A * 0 = 0
        # 0 * A = 0
        if lhs_is_empty or rhs_is_empty:
            return EmptyQueryNode()

        return AndQueryNode(lhs, rhs)


class IdempotentLaw(SimplificationRule):
    def visit_and(self, node: AndQueryNode) -> QueryNode:
        lhs = node.lhs.accept(self)
        rhs = node.rhs.accept(self)

        # A * A = A
        if lhs == rhs:
            return lhs

        return AndQueryNode(lhs, rhs)

    def visit_or(self, node: OrQueryNode) -> QueryNode:
        lhs = node.lhs.accept(self)
        rhs = node.rhs.accept(self)

        # A + A = A
        if lhs == rhs:
            return lhs

        return OrQueryNode(lhs, rhs)


class ComplementLaw(SimplificationRule):
    def visit_and(self, node: AndQueryNode) -> QueryNode:
        lhs = node.lhs.accept(self)
        rhs = node.rhs.accept(self)

        lhs_is_not = isinstance(lhs, NotQueryNode)
        rhs_is_not = isinstance(rhs, NotQueryNode)

        # !A * A = 0
        # A * !A = 0
        if lhs_is_not and lhs.child == rhs:
            return EmptyQueryNode()
        if rhs_is_not and rhs.child == lhs:
            return EmptyQueryNode()

        return AndQueryNode(lhs, rhs)

    def visit_or(self, node: OrQueryNode) -> QueryNode:
        lhs = node.lhs.accept(self)
        rhs = node.rhs.accept(self)

        lhs_is_not = isinstance(lhs, NotQueryNode)
        rhs_is_not = isinstance(rhs, NotQueryNode)

        # !A + A = A
        # A + !A = A
        if lhs_is_not and lhs.child == rhs:
            return rhs
        if rhs_is_not and rhs.child == lhs:
            return lhs

        return OrQueryNode(lhs, rhs)


class InvolutionLaw(SimplificationRule):
    def visit_not(self, node: NotQueryNode) -> QueryNode:
        child = node.child.accept(self)

        # !0 = 0, given that our logic does not map 1:1 to Boolean Algebra
        if isinstance(child, EmptyQueryNode):
            return EmptyQueryNode()

        # !!A = A
        if isinstance(child, NotQueryNode):
            return child.child

        return NotQueryNode(child)


class CommutativeLaw(SimplificationRule):
    def visit_and(self, node: AndQueryNode) -> QueryNode:
        lhs = node.lhs.accept(self)
        rhs = node.rhs.accept(self)

        # A * B = B * A
        if random.random() < 0.5:
            return AndQueryNode(lhs, rhs)
        return AndQueryNode(rhs, lhs)

    def visit_or(self, node: OrQueryNode) -> QueryNode:
        lhs = node.lhs.accept(self)
        rhs = node.rhs.accept(self)

        # A + B = B + A
        if random.random() < 0.5:
            return OrQueryNode(lhs, rhs)
        return OrQueryNode(rhs, lhs)


class AssociativeLaw(SimplificationRule):
    def visit_and(self, node: AndQueryNode) -> QueryNode:
        lhs = node.lhs.accept(self)
        rhs = node.rhs.accept(self)

        lhs_is_and = isinstance(lhs, AndQueryNode)
        rhs_is_and = isinstance(rhs, AndQueryNode)

        if not (lhs_is_and or rhs_is_and):
            return AndQueryNode(lhs, rhs)

        if random.random() < 0.5:
            return AndQueryNode(lhs, rhs)

        # (A * B) * C = A * (B * C)
        if lhs_is_and:
            return AndQueryNode(lhs.lhs, AndQueryNode(lhs.rhs, rhs))
        if rhs_is_and:
            return AndQueryNode(AndQueryNode(lhs, rhs.lhs), rhs.rhs)

        return AndQueryNode(lhs, rhs)

    def visit_or(self, node: OrQueryNode) -> QueryNode:
        lhs = node.lhs.accept(self)
        rhs = node.rhs.accept(self)

        lhs_is_or = isinstance(lhs, OrQueryNode)
        rhs_is_or = isinstance(rhs, OrQueryNode)

        if not (lhs_is_or or rhs_is_or):
            return OrQueryNode(lhs, rhs)

        if random.random() < 0.5:
            return OrQueryNode(lhs, rhs)

        # (A + B) + C = A + (B + C)
        if lhs_is_or:
            return OrQueryNode(lhs.lhs, OrQueryNode(lhs.rhs, rhs))
        if rhs_is_or:
            return OrQueryNode(OrQueryNode(lhs, rhs.lhs), rhs.rhs)

        return OrQueryNode(lhs, rhs)


class DistributiveLaw(SimplificationRule):
    def visit_and(self, node: AndQueryNode) -> QueryNode:
        lhs = node.lhs.accept(self)
        rhs = node.rhs.accept(self)

        lhs_is_and = isinstance(lhs, AndQueryNode)
        rhs_is_and = isinstance(rhs, AndQueryNode)

        if lhs_is_and and rhs_is_and:
            # (A * B) * (A * C) = A * (B * C)
            # (A * B) * (C * A) = A * (B * C)
            # (B * A) * (A * C) = A * (B * C)
            # (B * A) * (C * A) = A * (B * C)
            if lhs.lhs == rhs.lhs:
                return AndQueryNode(lhs.lhs, AndQueryNode(lhs.rhs, rhs.rhs))
            if lhs.lhs == rhs.rhs:
                return AndQueryNode(lhs.lhs, AndQueryNode(lhs.rhs, rhs.lhs))
            if lhs.rhs == rhs.lhs:
                return AndQueryNode(lhs.rhs, AndQueryNode(lhs.lhs, rhs.rhs))
            if lhs.rhs == rhs.rhs:
                return AndQueryNode(lhs.rhs, AndQueryNode(lhs.lhs, rhs.lhs))

        lhs_is_or = isinstance(lhs, OrQueryNode)
        rhs_is_or = isinstance(rhs, OrQueryNode)

        if lhs_is_or and rhs_is_or:
            # (A + B) * (A + C) = A + (B * C)
            # (A + B) * (C + A) = A + (B * C)
            # (B + A) * (A + C) = A + (B * C)
            # (B + A) * (C + A) = A + (B * C)
            if lhs.lhs == rhs.lhs:
                return OrQueryNode(lhs.lhs, AndQueryNode(lhs.rhs, rhs.rhs))
            if lhs.lhs == rhs.rhs:
                return OrQueryNode(lhs.lhs, AndQueryNode(lhs.rhs, rhs.lhs))
            if lhs.rhs == rhs.lhs:
                return OrQueryNode(lhs.rhs, AndQueryNode(lhs.lhs, rhs.rhs))
            if lhs.rhs == rhs.rhs:
                return OrQueryNode(lhs.rhs, AndQueryNode(lhs.lhs, rhs.lhs))

        return AndQueryNode(lhs, rhs)

    def visit_or(self, node: OrQueryNode) -> QueryNode:
        lhs = node.lhs.accept(self)
        rhs = node.rhs.accept(self)

        lhs_is_and = isinstance(lhs, AndQueryNode)
        rhs_is_and = isinstance(rhs, AndQueryNode)

        if lhs_is_and and rhs_is_and:
            # (A * B) + (A * C) = A * (B + C)
            # (A * B) + (C * A) = A * (B + C)
            # (B * A) + (A * C) = A * (B + C)
            # (B * A) + (C * A) = A * (B + C)
            if lhs.lhs == rhs.lhs:
                return AndQueryNode(lhs.lhs, OrQueryNode(lhs.rhs, rhs.rhs))
            if lhs.lhs == rhs.rhs:
                return AndQueryNode(lhs.lhs, OrQueryNode(lhs.rhs, rhs.lhs))
            if lhs.rhs == rhs.lhs:
                return AndQueryNode(lhs.rhs, OrQueryNode(lhs.lhs, rhs.rhs))
            if lhs.rhs == rhs.rhs:
                return AndQueryNode(lhs.rhs, OrQueryNode(lhs.lhs, rhs.lhs))

        lhs_is_or = isinstance(lhs, AndQueryNode)
        rhs_is_or = isinstance(rhs, AndQueryNode)

        if lhs_is_or and rhs_is_or:
            # (A + B) + (A + C) = A + (B + C)
            # (A + B) + (C + A) = A + (B + C)
            # (B + A) + (A + C) = A + (B + C)
            # (B + A) + (C + A) = A + (B + C)
            if lhs.lhs == rhs.lhs:
                return OrQueryNode(lhs.lhs, OrQueryNode(lhs.rhs, rhs.rhs))
            if lhs.lhs == rhs.rhs:
                return OrQueryNode(lhs.lhs, OrQueryNode(lhs.rhs, rhs.lhs))
            if lhs.rhs == rhs.lhs:
                return OrQueryNode(lhs.rhs, OrQueryNode(lhs.lhs, rhs.rhs))
            if lhs.rhs == rhs.rhs:
                return OrQueryNode(lhs.rhs, OrQueryNode(lhs.lhs, rhs.lhs))

        return OrQueryNode(lhs, rhs)


class AbsorptionLaw(SimplificationRule):
    def visit_and(self, node: AndQueryNode) -> QueryNode:
        lhs = node.lhs.accept(self)
        rhs = node.rhs.accept(self)

        lhs_is_or = isinstance(lhs, OrQueryNode)
        rhs_is_or = isinstance(rhs, OrQueryNode)

        if not (lhs_is_or or rhs_is_or):
            return AndQueryNode(lhs, rhs)

        # A * (A + B) = A
        # A * (B + A) = A
        # (A + B) * A = A
        # (B + A) * A = A
        if rhs_is_or and (lhs == rhs.lhs or lhs == rhs.rhs):
            return lhs
        if lhs_is_or and (rhs == lhs.lhs or rhs == lhs.rhs):
            return rhs

        return AndQueryNode(lhs, rhs)

    def visit_or(self, node: OrQueryNode) -> QueryNode:
        lhs = node.lhs.accept(self)
        rhs = node.rhs.accept(self)

        lhs_is_and = isinstance(lhs, AndQueryNode)
        rhs_is_and = isinstance(rhs, AndQueryNode)

        if not (lhs_is_and or rhs_is_and):
            return OrQueryNode(lhs, rhs)

        # A * (A + B) = A
        # A * (B + A) = A
        # (A + B) * A = A
        # (B + A) * A = A
        if rhs_is_and and (lhs == rhs.lhs or lhs == rhs.rhs):
            return lhs
        if lhs_is_and and (rhs == lhs.lhs or rhs == lhs.rhs):
            return rhs

        return OrQueryNode(lhs, rhs)


class ReductionLaw(SimplificationRule):
    def visit_and(self, node: AndQueryNode) -> QueryNode:
        lhs = node.lhs.accept(self)
        rhs = node.rhs.accept(self)

        lhs_is_or = isinstance(lhs, OrQueryNode)
        rhs_is_or = isinstance(rhs, OrQueryNode)

        if not (lhs_is_or and rhs_is_or):
            return AndQueryNode(lhs, rhs)

        # (A + B) * (A + !B) = A
        # (A + !B) * (A + B) = A
        if lhs.lhs == rhs.lhs:
            lhs_rhs_is_not = isinstance(lhs.rhs, NotQueryNode)
            rhs_rhs_is_not = isinstance(rhs.rhs, NotQueryNode)

            if (lhs_rhs_is_not and lhs.rhs.child == rhs.rhs or
                    rhs_rhs_is_not and rhs.rhs.child == lhs.rhs):
                return lhs.lhs

        # (A + B) * (!B + A) = A
        # (A + !B) * (B + A) = A
        if lhs.lhs == rhs.rhs:
            lhs_rhs_is_not = isinstance(lhs.rhs, NotQueryNode)
            rhs_lhs_is_not = isinstance(rhs.lhs, NotQueryNode)

            if (lhs_rhs_is_not and lhs.rhs.child == rhs.lhs or
                    rhs_lhs_is_not and rhs.lhs.child == lhs.rhs):
                return lhs.lhs

        # (B + A) * (A + !B) = A
        # (!B + A) * (A + B) = A
        if lhs.rhs == rhs.lhs:
            lhs_lhs_is_not = isinstance(lhs.rhs, NotQueryNode)
            rhs_rhs_is_not = isinstance(rhs.lhs, NotQueryNode)

            if (lhs_lhs_is_not and lhs.lhs.child == rhs.rhs or
                    rhs_rhs_is_not and rhs.rhs.child == lhs.lhs):
                return lhs.lhs

        # (B + A) * (!B + A) = A
        # (!B + A) * (B + A) = A
        if lhs.rhs == rhs.lhs:
            lhs_lhs_is_not = isinstance(lhs.rhs, NotQueryNode)
            rhs_lhs_is_not = isinstance(rhs.lhs, NotQueryNode)

            if (lhs_lhs_is_not and lhs.lhs.child == rhs.rhs or
                    rhs_lhs_is_not and rhs.lhs.child == lhs.lhs):
                return lhs.lhs

        return AndQueryNode(lhs, rhs)

    def visit_or(self, node: OrQueryNode) -> QueryNode:
        lhs = node.lhs.accept(self)
        rhs = node.rhs.accept(self)

        lhs_is_and = isinstance(lhs, AndQueryNode)
        rhs_is_and = isinstance(rhs, AndQueryNode)

        if not (lhs_is_and and rhs_is_and):
            return OrQueryNode(lhs, rhs)

        # (A * B) + (A * !B) = A
        # (A * !B) + (A * B) = A
        if lhs.lhs == rhs.lhs:
            lhs_rhs_is_not = isinstance(lhs.rhs, NotQueryNode)
            rhs_rhs_is_not = isinstance(rhs.rhs, NotQueryNode)

            if (lhs_rhs_is_not and lhs.rhs.child == rhs.rhs or
                    rhs_rhs_is_not and rhs.rhs.child == lhs.rhs):
                return lhs.lhs

        # (A * B) + (!B * A) = A
        # (A * !B) + (B * A) = A
        if lhs.lhs == rhs.rhs:
            lhs_rhs_is_not = isinstance(lhs.rhs, NotQueryNode)
            rhs_lhs_is_not = isinstance(rhs.lhs, NotQueryNode)

            if (lhs_rhs_is_not and lhs.rhs.child == rhs.lhs or
                    rhs_lhs_is_not and rhs.lhs.child == lhs.rhs):
                return lhs.lhs

        # (B * A) + (A * !B) = A
        # (!B * A) + (A * B) = A
        if lhs.rhs == rhs.lhs:
            lhs_lhs_is_not = isinstance(lhs.rhs, NotQueryNode)
            rhs_rhs_is_not = isinstance(rhs.lhs, NotQueryNode)

            if (lhs_lhs_is_not and lhs.lhs.child == rhs.rhs or
                    rhs_rhs_is_not and rhs.rhs.child == lhs.lhs):
                return lhs.lhs

        # (B * A) + (!B * A) = A
        # (!B * A) + (B * A) = A
        if lhs.rhs == rhs.lhs:
            lhs_lhs_is_not = isinstance(lhs.rhs, NotQueryNode)
            rhs_lhs_is_not = isinstance(rhs.lhs, NotQueryNode)

            if (lhs_lhs_is_not and lhs.lhs.child == rhs.rhs or
                    rhs_lhs_is_not and rhs.lhs.child == lhs.lhs):
                return lhs.lhs

        return OrQueryNode(lhs, rhs)


class DeMorgansLaw(SimplificationRule):
    def visit_and(self, node: AndQueryNode) -> QueryNode:
        lhs = node.lhs.accept(self)
        rhs = node.rhs.accept(self)

        lhs_is_not = isinstance(lhs, NotQueryNode)
        rhs_is_not = isinstance(rhs, NotQueryNode)

        if not (lhs_is_not and rhs_is_not):
            return AndQueryNode(lhs, rhs)

        # !A * !B = !(A + B)
        if random.random() < 0.5:
            return AndQueryNode(lhs, rhs)
        return NotQueryNode(OrQueryNode(lhs.child, rhs.child))

    def visit_or(self, node: OrQueryNode) -> QueryNode:
        lhs = node.lhs.accept(self)
        rhs = node.rhs.accept(self)

        lhs_is_not = isinstance(lhs, NotQueryNode)
        rhs_is_not = isinstance(rhs, NotQueryNode)

        if not (lhs_is_not and rhs_is_not):
            return OrQueryNode(lhs, rhs)

        # !A + !B = !(A * B)
        if random.random() < 0.5:
            return OrQueryNode(lhs, rhs)
        return NotQueryNode(AndQueryNode(lhs.child, rhs.child))

    def visit_not(self, node: NotQueryNode) -> QueryNode:
        child = node.child.accept(self)

        # !(A * B) = !A + !B
        # !(A + B) = !A * !B
        if isinstance(child, AndQueryNode):
            if random.random() < 0.5:
                return NotQueryNode(child)
            return OrQueryNode(NotQueryNode(child.lhs), NotQueryNode(child.rhs))
        if isinstance(child, OrQueryNode):
            if random.random() < 0.5:
                return NotQueryNode(child)
            return OrQueryNode(NotQueryNode(child.lhs), NotQueryNode(child.rhs))

        return NotQueryNode(child)


class HeightQueryNodeVisitor(QueryNodeVisitor):
    def visit_word(self, node: WordQueryNode, height: int = 0) -> int:
        return height

    def visit_and(self, node: AndQueryNode, height: int = 0) -> int:
        return max(node.lhs.accept(self, height + 1), node.rhs.accept(self, height + 1))

    def visit_or(self, node: OrQueryNode, height: int = 0) -> int:
        return max(node.lhs.accept(self, height + 1), node.rhs.accept(self, height + 1))

    def visit_not(self, node: NotQueryNode, height: int = 0) -> int:
        return node.child.accept(self, height + 1)

    def visit_empty(self, node: EmptyQueryNode, height: int = 0) -> int:
        return height


class CountQueryNodeVisitor(QueryNodeVisitor):
    def visit_word(self, node: WordQueryNode) -> int:
        return 1

    def visit_and(self, node: AndQueryNode) -> int:
        return node.lhs.accept(self) + node.rhs.accept(self) + 1

    def visit_or(self, node: OrQueryNode) -> int:
        return node.lhs.accept(self) + node.rhs.accept(self) + 1

    def visit_not(self, node: NotQueryNode) -> int:
        return node.child.accept(self) + 1

    def visit_empty(self, node: EmptyQueryNode) -> int:
        return 1


class SimplifyingQueryNodeVisitor(SimplificationRule):
    def __init__(self):
        self._simplification_rules = [
            IdentityLaw(),
            DominationLaw(),
            IdempotentLaw(),
            ComplementLaw(),
            InvolutionLaw(),
            DistributiveLaw(),
            AbsorptionLaw(),
            ReductionLaw()
        ]

        self._reordering_rules = [
            CommutativeLaw(),
            AssociativeLaw(),
            DeMorgansLaw()
        ]

    def visit_word(self, node: WordQueryNode) -> QueryNode:
        return self._simplify(node)

    def visit_and(self, node: AndQueryNode) -> QueryNode:
        return self._simplify(node)

    def visit_or(self, node: OrQueryNode) -> QueryNode:
        return self._simplify(node)

    def visit_not(self, node: NotQueryNode) -> QueryNode:
        return self._simplify(node)

    def visit_empty(self, node: EmptyQueryNode) -> QueryNode:
        return self._simplify(node)

    def _simplify(self, node: QueryNode) -> QueryNode:
        tree_size = node.accept(CountQueryNodeVisitor())

        max_attempts = 1
        attempts = 0

        simplification_iterations = tree_size
        reordering_iterations = tree_size

        max_trees_in_queue = simplification_iterations * reordering_iterations
        new_trees = [node]

        best_tree = node
        for i in progress(range(tree_size)):
            reordered_trees = []
            for new_tree in new_trees:
                reordered_trees.extend([self._apply_reordering_rules(new_tree) for _ in range(reordering_iterations)])
            simplified_trees = []
            for new_tree in set(reordered_trees):
                simplified_tree = new_tree
                for _ in range(simplification_iterations):
                    tree_before_simplification = simplified_tree
                    simplified_tree = self._apply_simplification_rules(simplified_tree)
                    if simplified_tree == tree_before_simplification:
                        break
                simplified_trees.append(simplified_tree)
            new_trees = sorted(set(simplified_trees), key=lambda x: x.accept(CountQueryNodeVisitor()))[
                        :max_trees_in_queue]
            best_new_tree = new_trees[0]

            if best_new_tree == best_tree:
                attempts += 1
                if attempts == max_attempts:
                    return best_tree

            best_tree = best_new_tree

            if len(simplified_trees) == 1:
                break

        return best_tree

    def _apply_simplification_rules(self, node: QueryNode) -> QueryNode:
        for rule in self._simplification_rules:
            node = node.accept(rule)
        return node

    def _apply_reordering_rules(self, node: QueryNode) -> QueryNode:
        for rule in self._reordering_rules:
            node = node.accept(rule)
        return node


class SimpleQuerySimplifier(QuerySimplifier):
    def __init__(self):
        self._simplifying_visitor = SimplifyingQueryNodeVisitor()

    def simplify_query(self, query_node: QueryNode) -> QueryNode:
        simplified = query_node.accept(self._simplifying_visitor)
        return simplified


DEFAULT_QUERY_SIMPLIFIER = SimpleQuerySimplifier()


def default_query_simplifier():
    return DEFAULT_QUERY_SIMPLIFIER
