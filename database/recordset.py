from abc import ABC, abstractmethod
from typing import Iterable, Iterator, Tuple, List, Any

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

    def join(self, other: 'RecordSet', self_key: Expression[Any], other_key: Expression[Any]) -> 'Join':
        return Join(self, other, self_key, other_key)

    def display(self) -> None:
        headers = [expr.name for expr in self.expressions]
        rows = []
        for record in self:
            row = []
            for expr in self.expressions:
                value = record[expr.name]
                row.append(str(value))
            rows.append(row)

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
            data = dict[str, Any]()
            for expression in self.expressions:
                if isinstance(expression, Aggregation):
                    data[expression.name] = record[expression.name]
                else:
                    data[expression.name] = expression.evaluate(record)
            yield Record(data, self.expressions)


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
            left_key: Expression,
            right_key: Expression
    ):
        combined_expressions = list(left.expressions) + list(right.expressions)
        super().__init__(combined_expressions)
        self._left = left
        self._right = right
        self._compiled_left_key = left_key.compile()
        self._compiled_right_key = right_key.compile()

    def __iter__(self) -> Iterator[Record]:
        hash_table = dict[Any, List[Record]]()
        for right_record in self._right:
            key = self._compiled_right_key(right_record)
            if key not in hash_table:
                hash_table[key] = list[Record]()
            hash_table[key].append(right_record)

        for left_record in self._left:
            key = self._compiled_left_key(left_record)
            matches = hash_table.get(key, [])
            for right_record in matches:
                data = {expression.name: left_record[expression] for expression in self._left.expressions}
                data.update({expression.name: right_record[expression] for expression in self._right.expressions})
                yield Record(data, self.expressions)
