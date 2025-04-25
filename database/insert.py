from typing import Self, Any

from database.table import Table


class Insert:
    def __init__(self, table: Table):
        self._table = table
        self._values = dict[str, Any]()

    def values_map(self, **kwargs) -> Self:
        self._values.update(kwargs)
        return self

    def execute(self) -> None:
        self._table.insert(**self._values)
