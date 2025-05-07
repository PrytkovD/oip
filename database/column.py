from typing import Callable, Optional, Type

from database.expression import Expression
from database.record import Record


class Column[T](Expression[T]):
    def __init__(self, name: str, type: Type[T]):
        super().__init__()
        self._table: Optional['Table'] = None
        self._name = name
        self._type = type

    @property
    def table(self) -> Optional['Table']:
        return self._table

    @property
    def own_name(self) -> str:
        return self._name

    @table.setter
    def table(self, table: 'Table'):
        self._table = table

    @property
    def type(self):
        return self._type

    def _evaluate(self, record: Record) -> T:
        try:
            return record[self.name]
        except KeyError:
            return record[self.original_name]

    def _compile(self) -> Callable[[Record], T]:
        return lambda record: record[self.name] if self.name in record else record[self.original_name]

    def _get_name(self):
        return f'{self._table.name}.{self._name}' if self._table is not None else self._name


from database.table import Table
