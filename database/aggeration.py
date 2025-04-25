from abc import ABC, abstractmethod
from typing import Callable, Optional, List, Dict, Any

from database.expression import Expression


class Aggregation[T, U](Expression[List[U]], ABC):
    def __init__(self, expression: Optional[Expression[U]] = None):
        super().__init__()
        self._expression = expression
        self._compiled_aggregation: Optional[Callable[[List[Record]], T]] = None

    @classmethod
    def sum(cls, expression: Expression[T]) -> 'SumAggregation[T]':
        return SumAggregation(expression)

    @classmethod
    def count(cls, expression: Optional[Expression[U]] = None) -> 'CountAggregation':
        return CountAggregation(expression)

    @classmethod
    def list(cls, expression: Expression[T]) -> 'ListAggregation[T]':
        return ListAggregation(expression)

    @classmethod
    def dict(cls, *expressions: Expression[T]) -> 'DictAggregation':
        return DictAggregation(*expressions)

    def _evaluate(self, record: 'Record') -> List[U]:
        return record[self.name]

    def _compile(self) -> Callable[['Record'], List[U]]:
        return lambda record: record[self.name]

    def aggregate(self, records: List['Record']) -> T:
        if self._compiled_aggregation is None:
            return self._aggregate(records)
        else:
            return self._compiled_aggregation(records)

    def compile_aggregation(self) -> Callable[[List['Record']], T]:
        if self._compiled_aggregation is None:
            self._compiled_aggregation = self._compile_aggregation()
        return self._compiled_aggregation

    @abstractmethod
    def _aggregate(self, records: List['Record']) -> T:
        return NotImplemented

    @abstractmethod
    def _compile_aggregation(self) -> Callable[[List['Record']], U]:
        return NotImplemented


class SumAggregation[T](Aggregation[T, T]):
    def __init__(self, expression: Expression[T]):
        super().__init__(expression)

    def _aggregate(self, records: List['Record']) -> T:
        return sum(self._expression.evaluate(record) for record in records)

    def _compile_aggregation(self) -> Callable[[List['Record']], T]:
        compiled_expression = self._expression.compile()
        return lambda records: sum(compiled_expression(record) for record in records)

    def _get_name(self):
        return f'sum({self._expression.name})'


class CountAggregation[T](Aggregation[int, T]):
    def _aggregate(self, records: List['Record']) -> int:
        if self._expression is None:
            return len(records)

        return sum(int(self._expression in record) for record in records)

    def _compile_aggregation(self) -> Callable[[List['Record']], int]:
        if self._expression is None:
            return lambda records: len(records)

        return lambda records: sum(int(self._expression in record) for record in records)

    def _get_name(self):
        return f'count({self._expression.name})' if self._expression is not None else 'count()'


class ListAggregation[T](Aggregation[List[T], T]):
    def __init__(self, expression: Expression[T]):
        super().__init__(expression)

    def _aggregate(self, records: List['Record']) -> List[T]:
        return [self._expression.evaluate(record) for record in records]

    def _compile_aggregation(self) -> Callable[[List['Record']], List[T]]:
        compiled_expression = self._expression.compile()
        return lambda records: [compiled_expression(record) for record in records]

    def _get_name(self):
        return f'list({self._expression.name})'


class DictAggregation[T](Aggregation[Dict[str, Any], T]):
    def __init__(self, *expressions: Expression):
        super().__init__()
        self._expressions = expressions

    def _aggregate(self, records: List['Record']) -> Dict[str, Any]:
        return {_expression.name: record[_expression]
                for _expression in self._expressions
                for record in records}

    def _compile_aggregation(self) -> Callable[[List['Record']], Dict[str, Any]]:
        for expression in self._expressions:
            expression.compile()
        return lambda records: {_expression.name: record[_expression]
                                for _expression in self._expressions
                                for record in records}

    def _get_name(self):
        return f'dict({', '.join([str(expression.name) for expression in self._expressions])})'


from database.record import Record
