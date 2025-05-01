from typing import Callable, Optional

from database.expression import Expression
from database.record import Record


class Column[T](Expression[T]):
    def __init__(self, name: str):
        super().__init__()
        self._table: Optional['Table'] = None
        self._name = name

    @property
    def table(self) -> Optional['Table']:
        return self._table

    @property
    def own_name(self) -> str:
        return self._name

    @table.setter
    def table(self, table: 'Table'):
        self._table = table

    def _evaluate(self, record: Record) -> T:
        return record[self.name]

    def _compile(self) -> Callable[[Record], T]:
        return lambda record: record[self.name]

    def _get_name(self):
        return f'{self._table.name}.{self._name}' if self._table is not None else self._name


from database.table import Table
