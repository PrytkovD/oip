from abc import ABC, abstractmethod
from typing import Iterable, Iterator, Tuple, List, Any, Optional

from database.aggeration import Aggregation
from database.columnset import ColumnSet, ColumnSelector
from database.expression import Expression, RawExpression
from database.record import Record


class RecordSet(ColumnSet, ABC):
    def __init__(self, expressions: Iterable[Expression]):
        super().__init__(expressions)

    @abstractmethod
    def __iter__(self) -> Iterator[Record]:
        ...

    def select(self, *expressions: ColumnSelector) -> 'Projection':
        return Projection(self, list(expression if isinstance(expression, Expression) else RawExpression(expression)
                                     for expression in expressions))

    def where(self, predicate: Expression[bool]) -> 'Filter':
        if predicate.name not in self.expressions:
            raise ValueError(f'{predicate.name} is not in the column set')
        return Filter(self, predicate)

    def aggregate(self, *aggregations: Aggregation) -> 'Aggregated':
        return Aggregated(self, list(aggregations))

    def order_by(self, *orderings: Expression | Tuple[Expression, bool]) -> 'OrderBy':
        fixed_orderings = list[Tuple[Expression, bool]]()

        for ordering in orderings:
            if isinstance(ordering, tuple):
                expression, reverse = ordering
            else:
                expression, reverse = ordering, False

            fixed_orderings.append((expression, reverse))

            if expression.name not in self.expressions:
                raise ValueError(f'{expression.name} is not in the column set')

        return OrderBy(self, fixed_orderings)

    def group_by(self, *expressions: ColumnSelector) -> 'GroupBy':
        return GroupBy(self, list(expression if isinstance(expression, Expression) else RawExpression(expression)
                                  for expression in expressions))

    def join(
            self,
            other: 'RecordSet',
            self_key: Optional[Expression],
            other_key: Optional[Expression],
            condition: Optional[Expression[bool]],
            join_type: str = 'inner'
    ) -> 'Join':
        return Join(self, other, self_key, other_key, condition, join_type)

    def display(self, max_records: Optional[int] = None) -> None:
        headers = [expr.name for expr in self.expressions]
        rows = []
        for record in self:
            row = []
            for expr in self.expressions:
                value = record[expr.name]
                row.append(str(value))
            rows.append(row)
            if max_records is not None and len(rows) >= max_records:
                break

        max_widths = [len(header) for header in headers]
        for row in rows:
            for i, value_str in enumerate(row):
                current_length = len(value_str)
                if current_length > max_widths[i]:
                    max_widths[i] = current_length

        format_str = "  ".join(f"%-{width}s" for width in max_widths)

        print(format_str % tuple(headers))

        for row in rows:
            print(format_str % tuple(row))


class SimpleResultSet(RecordSet):
    def __init__(self, records: Iterable[Record], expressions: Iterable[Expression]):
        super().__init__(expressions)
        self._records = records

    def __iter__(self) -> Iterator[Record]:
        for record in self._records:
            yield record


class Projection(RecordSet):
    def __init__(self, source: RecordSet, expressions: Iterable[Expression]):
        super().__init__(expressions)
        self._source = source

        for expression in self.expressions:
            if not isinstance(expression, Aggregation):
                expression.compile()

    def __iter__(self) -> Iterator[Record]:
        for record in self._source:
            yield self._make_record(record)

    def _make_record(self, record: Record) -> Record:
        data = dict[str, Any]()
        for expression in self.expressions:
            value = None
            if isinstance(expression, Aggregation):
                try:
                    value = record[expression.name]
                except KeyError:
                    value = record[expression.original_name]
            else:
                value = expression.evaluate(record)
            data[expression.name] = value
        return Record(data, self.expressions)


class Filter(RecordSet):
    def __init__(self, source: RecordSet, predicate: Expression[bool]):
        super().__init__(source.expressions)
        self._source = source
        self._predicate = predicate

        self._predicate.compile()

    def __iter__(self) -> Iterator[Record]:
        for record in self._source:
            if self._predicate.evaluate(record):
                yield record


class OrderBy(RecordSet):
    def __init__(self, source: RecordSet, orderings: List[Tuple[Expression, bool]]):
        super().__init__(source.expressions)
        self._source = source
        self._orderings = orderings

        for ordering in self._orderings:
            expression, _ = ordering
            if not isinstance(expression, Aggregation):
                expression.compile()

    def __iter__(self) -> Iterator[Record]:
        records = list(self._source)

        def get_sort_key(record: Record):
            return tuple(
                (-expression.evaluate(record) if reverse else expression.evaluate(record))
                for expression, reverse in self._orderings
            )

        for records in sorted(records, key=get_sort_key):
            yield records


class Aggregated(RecordSet):
    def __init__(self, source: RecordSet, aggregations: Iterable[Aggregation]):
        super().__init__(aggregations)
        self._source = source
        self._aggregations = aggregations

        for aggregation in self._aggregations:
            aggregation.compile_aggregation()

    def __iter__(self) -> Iterator[Record]:
        data = dict[str, Any]()
        for aggregation in self._aggregations:
            data[aggregation.name] = aggregation.aggregate(list(self._source))
        yield Record(data, self.expressions)


class GroupBy:
    def __init__(self, source: RecordSet, expressions: Iterable[Expression]):
        self._source = source
        self._expressions = expressions

        for expression in self._expressions:
            expression.compile()

    def aggregate(self, *aggregations: Aggregation) -> RecordSet:
        groups = dict[Tuple, List[Record]]()
        for record in self._source:
            key = tuple(expression.evaluate(record) for expression in self._expressions)
            if key not in groups:
                groups[key] = list[Record]()
            groups[key].append(record)

        result_expressions = list(self._expressions) + list(aggregations)
        results = list[Record]()
        for group, records in groups.items():
            data = {expression.name: group_value for expression, group_value in zip(self._expressions, group)}
            for aggregation in aggregations:
                compiled_aggregation = aggregation.compile_aggregation()
                data[aggregation.name] = compiled_aggregation(records)
            results.append(Record(data, result_expressions))

        return SimpleResultSet(results, result_expressions)


class Join(RecordSet):
    def __init__(
            self,
            left: RecordSet,
            right: RecordSet,
            left_key: Optional[Expression] = None,
            right_key: Optional[Expression] = None,
            condition: Optional[Expression[bool]] = None,
            join_type: str = 'inner'
    ):
        combined_expressions = list(left.expressions) + list(right.expressions)
        super().__init__(combined_expressions)

        self._left = left
        self._right = right

        self._compiled_left_key = left_key.compile() if left_key is not None else None
        self._compiled_right_key = right_key.compile() if right_key is not None else None
        self._compiled_condition = condition.compile() if condition is not None else None

        self._join_type = join_type

    def __iter__(self) -> Iterator[Record]:
        if self._join_type == 'cross':
            yield from self._cross_join()
            return
        elif self._compiled_left_key and self._compiled_right_key:
            yield from self._hash_join()
            return
        elif self._compiled_condition:
            yield from self._conditional_join()
            return
        else:
            raise NotImplementedError

    def _cross_join(self):
        for left_record in self._left:
            for right_record in self._right:
                yield self._make_record(left_record, right_record)

    def _hash_join(self):
        hash_table = dict[Any, List[Record]]()
        for right_record in self._right:
            key = self._compiled_right_key(right_record)
            if key not in hash_table:
                hash_table[key] = list[Record]()
            hash_table[key].append(right_record)

        matched_right_ids = set[int]()

        for left_record in self._left:
            key = self._compiled_left_key(left_record)
            matches = hash_table.get(key, [])

            if matches:
                for right_record in matches:
                    matched_right_ids.add(id(right_record))
                    yield self._make_record(left_record, right_record)
            elif self._join_type in ('left', 'full'):
                yield self._make_record(left_record, None)

        if self._join_type in ('right', 'full'):
            for right_record in self._right:
                if id(right_record) not in matched_right_ids:
                    yield self._make_record(None, right_record)

    def _conditional_join(self):
        matched_right_ids = set()
        matched_left_ids = set()
        right_records = list(self._right)
        left_records = list(self._left)

        for left_record in left_records:
            match_found = False
            for right_record in right_records:
                record = self._make_record(left_record, right_record)
                if self._compiled_condition(record):
                    match_found = True
                    matched_right_ids.add(id(right_record))
                    matched_left_ids.add(id(left_record))
                    yield record
            if not match_found and self._join_type in ("left", "full"):
                yield self._make_record(left_record, None)

        if self._join_type in ("right", "full"):
            for right_record in right_records:
                if id(right_record) not in matched_right_ids:
                    yield self._make_record(None, right_record)

    def _make_record(self, left_record: Record | None, right_record: Record | None) -> Record:
        data: dict[str, Any] = {}
        for expression in self._left.expressions:
            data[expression.name] = left_record[expression] if left_record is not None else None
        for expression in self._right.expressions:
            data[expression.name] = right_record[expression] if right_record is not None else None
        return Record(data, self.expressions)
