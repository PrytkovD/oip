from abc import ABC
from typing import Iterable, Dict, List, Self

from database.expression import Expression

type ColumnSelector = Expression | str


class ColumnSet(ABC):
    def __init__(self, expressions: Iterable[Expression]):
        self._columns: Dict[str, Expression] = {expr.name: expr for expr in expressions}

    @property
    def expressions(self) -> List[Expression]:
        return list(self._columns.values())

    def __contains__(self, expression: ColumnSelector) -> bool:
        key = expression.name if isinstance(expression, Expression) else expression
        return key in self._columns

    def __getitem__(self, key: ColumnSelector | Iterable[ColumnSelector]) -> Self:
        if isinstance(key, Expression | str):
            key = [key]

        selected: List[Expression] = []
        for expression in key:
            if expression in self:
                selected.append(self._columns[expression])
            elif isinstance(expression, Expression):
                selected.append(expression)
            else:
                raise KeyError(f'Unsupported key type: {type(expression)}')

        return self.__class__(selected)
