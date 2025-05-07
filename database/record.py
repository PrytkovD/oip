from typing import Dict, Any, Iterable, Self, Optional

from database.columnset import ColumnSet, ColumnSelector
from database.expression import Expression, RawExpression


class Record(ColumnSet):
    def __init__(
            self,
            data: Dict[str, Any],
            expressions: Optional[Iterable[Expression]] = None
    ):
        expressions = expressions or (RawExpression(name) for name in data.keys())
        super().__init__(expressions)
        self._data = data

    def get(self, key: ColumnSelector) -> Any | None:
        if isinstance(key, Expression | str):
            key = key.name if isinstance(key, Expression) else key
            return self._data.get(key)

        return None

    def __getitem__(self, key: ColumnSelector | Iterable[ColumnSelector]) -> Self | Any:
        if isinstance(key, Expression | str):
            key = key.name if isinstance(key, Expression) else key
            return self._data[key]

        return super().__getitem__(key)

    def items(self):
        return self._data.items()

    def __str__(self):
        return str(self._data)
