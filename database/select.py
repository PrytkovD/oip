from typing import Optional, Self, Tuple

from database.aggeration import Aggregation
from database.columnset import ColumnSelector
from database.expression import Expression
from database.recordset import RecordSet


class Select:
    def __init__(self, source: RecordSet):
        self._source = source
        self._projections = list[Expression]()
        self._predicate: Optional[Expression[bool]] = None
        self._aggregations = list[Aggregation]()
        self._group_keys = list[ColumnSelector]()
        self._joins = list[Tuple[RecordSet, Expression, Expression, Expression[bool], str]]()
        self._orderings = None

    def columns(self, *exprs: Expression) -> Self:
        self._projections = list(exprs)
        return self

    def where(self, predicate: Expression[bool]) -> Self:
        self._predicate = predicate
        return self

    def group_by(self, *keys: ColumnSelector) -> Self:
        self._group_keys = list(keys)
        return self

    def aggregate(self, *aggs: Aggregation) -> Self:
        self._aggregations = list(aggs)
        return self

    def join(
            self,
            other: RecordSet,
            self_key: Optional[Expression] = None,
            other_key: Optional[Expression] = None,
            on: Optional[Expression[bool]] = None,
            join_type: str = 'inner'
    ) -> Self:
        self._joins.append((other, self_key, other_key, on, join_type))
        return self

    def inner_join(
            self,
            other: RecordSet,
            self_key: Optional[Expression] = None,
            other_key: Optional[Expression] = None,
            on: Optional[Expression[bool]] = None,
    ):
        return self.join(other, self_key, other_key, on, join_type='inner')

    def left_join(
            self,
            other: RecordSet,
            self_key: Optional[Expression] = None,
            other_key: Optional[Expression] = None,
            on: Optional[Expression[bool]] = None,
    ):
        return self.join(other, self_key, other_key, on, join_type='left')

    def right_join(
            self,
            other: RecordSet,
            self_key: Optional[Expression] = None,
            other_key: Optional[Expression] = None,
            on: Optional[Expression[bool]] = None,
    ):
        return self.join(other, self_key, other_key, on, join_type='right')

    def full_join(
            self,
            other: RecordSet,
            self_key: Optional[Expression] = None,
            other_key: Optional[Expression] = None,
            on: Optional[Expression[bool]] = None,
    ):
        return self.join(other, self_key, other_key, on, join_type='full')

    def cross_join(self, other: RecordSet):
        return self.join(other, None, None, join_type='cross')

    def order_by(self, *orderings: Expression | Tuple[Expression, bool]) -> Self:
        self._orderings = list(orderings)
        return self

    def execute(self) -> RecordSet:
        result = self._source

        for other, result_key, other_key, condition, join_type in self._joins:
            result = result.join(other, result_key, other_key, condition, join_type)

        if self._predicate:
            result = result.where(self._predicate)

        if self._aggregations:
            if self._group_keys:
                result = result.group_by(*self._group_keys).aggregate(*self._aggregations)
            else:
                result = result.aggregate(*self._aggregations)

        if self._projections:
            result = result.select(*self._projections)

        if self._orderings:
            result = result.order_by(*self._orderings)

        return result


def select_from(source: RecordSet) -> Select:
    return Select(source)
