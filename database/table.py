import atexit
from typing import Dict, Any, Iterator

from database.aliasmixin import AliasMixin
from database.columnset import ColumnSelector
from database.record import Record
from database.recordset import RecordSet


class Table(RecordSet, AliasMixin):
    def __init__(self, name: str, *columns: 'Column', page_size: int = 1000, storage_dir: str = '.',
                 cache_size: int = 10):
        super().__init__(list(columns))
        self._name = name
        self._storage = FilePageStorage(self, page_size, storage_dir, cache_size)

        for column in columns:
            column.table = self
            setattr(self, column.own_name, column)

        atexit.register(self.dump)

    def insert(
            self,
            record: Record | Dict[ColumnSelector, Any] | None = None,
            **kwargs: Any
    ):
        if isinstance(record, Record):
            data = {expr.name: record[expr] for expr in record.expressions}
        elif isinstance(record, dict):
            data = record.copy()
        else:
            data = {}
        data.update(kwargs)

        record = {expression.name: data[expression.name] for expression in self.expressions}
        self._storage.insert(record)

    def dump(self):
        self._storage.dump_all()

    def __iter__(self) -> Iterator[Record]:
        return self._storage.__iter__()

    def _get_name(self):
        return self._name


def create_table(name: str, *columns: str, page_size: int = 1000, storage_dir: str = '.', cache_size: int = 10):
    return Table(
        name,
        *[Column(column) for column in columns],
        page_size=page_size,
        storage_dir=storage_dir,
        cache_size=cache_size
    )


from database.storage import FilePageStorage
from database.column import Column
