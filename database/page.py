import csv
import os
from typing import Iterator, Dict, Any

from database.record import Record
from database.recordset import RecordSet


class Page(RecordSet):
    def __init__(self, table: 'Table', number: int, size: int, storage_dir: str):
        super().__init__(table.expressions)
        self._table = table
        self._number = number
        self._size = size
        self._storage_dir = storage_dir
        self._file_name = f'{self._table.name}_{self._number}.csv'
        self._file_path = os.path.join(storage_dir, self._file_name)
        self._records_data = list[Dict[str, Any]]()
        self._count = 0
        self._dirty = False

    @property
    def is_full(self) -> bool:
        return self._count == self._size

    def load(self):
        try:
            with open(self._file_path, 'r') as file:
                reader = csv.DictReader(file)
                self._records_data = [row for row in reader]
                self._count = len(self._records_data)
        except Exception:
            pass

    def dump(self):
        if not self._dirty:
            return

        with open(self._file_path, 'w') as file:
            writer = csv.DictWriter(
                file,
                fieldnames=[column.name for column in self._table.expressions],
                quoting=csv.QUOTE_ALL
            )
            writer.writeheader()
            writer.writerows(self._records_data)

        self._dirty = False

    def append(self, record_data: Dict[str, Any]):
        self._records_data.append(record_data)
        self._count += 1
        self._dirty = True

    def __iter__(self) -> Iterator[Record]:
        for record_data in self._records_data:
            yield Record(record_data, self.expressions)

    def __len__(self) -> int:
        return self._count


from database.table import Table
