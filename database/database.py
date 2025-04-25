# from __future__ import annotations
#
# import uuid
# from abc import ABC, abstractmethod
# from typing import List, Type, Dict, Any, Self, Optional, Mapping, Iterable
#
#
# class Database:
#     def __init__(self, name: str):
#         self._name = name
#         self._tables = list[Table]()
#
#     @property
#     def name(self) -> str:
#         return self._name
#
#     @property
#     def tables(self) -> List[Table]:
#         return self._tables
#
#     def create_table(self, name: str) -> Table:
#         table = Table(self, name)
#         self._tables.append(table)
#         setattr(self, name, table)
#         return table
#
#     def __eq__(self, other: object) -> bool:
#         if not isinstance(other, Database):
#             return False
#         return self.name == other.name
#
#     def __hash__(self) -> int:
#         return hash(self.name)
#
#     def __repr__(self):
#         return f'Database(\'{self._name}\'))'
#
#
# class ColumnSet(ABC):
#     def __init__(
#             self,
#             base: ColumnSet = None,
#             columns: List[Column] = None,
#             expressions: List[Expression] = None,
#             aggregations: List[Aggregation] = None
#     ):
#         self._base = base
#         self._columns = columns if columns is not None else list[Column]()
#         self._expressions = expressions if expressions is not None else list[Expression]()
#         self._aggregations = aggregations if aggregations is not None else list[Aggregation]()
#
#     @property
#     def base(self) -> Optional[ColumnSet]:
#         return self._base
#
#     @property
#     def tables(self) -> List[Table]:
#         columns = (set(self._columns) |
#                    set(column for expression in self._expressions for column in expression.columns) |
#                    set(column for aggregation in self._aggregations for column in aggregation.columns))
#         tables = list(set(column.table for column in columns))
#         return tables if len(tables) > 0 else self._base.tables if self._base is not None else []
#
#     @property
#     def columns(self) -> List[Column]:
#         columns = (set(self._columns) |
#                    set(column for aggregation in self._aggregations for column in aggregation.columns))
#         return list(columns)
#
#     @property
#     def expressions(self) -> List[Expression]:
#         return self._expressions
#
#     @property
#     def aggregations(self) -> List[Aggregation]:
#         return self._aggregations
#
#     def select(self, *expressions: ColumnLike) -> SelectStatement:
#         expressions = list(expressions)
#         only_aggregations = [expression for expression in expressions if isinstance(expression, Aggregation)]
#         only_expressions = [expression for expression in expressions if isinstance(expression, Expression)]
#         only_columns = [expression for expression in expressions if isinstance(expression, Column)]
#         select_set = ColumnSet(self, only_columns, only_expressions, only_aggregations)
#         return SelectStatement(select_set if len(expressions) > 0 else self)
#
#     def select_all(self, *expressions: ColumnLike) -> List[Record]:
#         return self.select(*expressions).execute()
#
#     def join(self, other: ColumnSet, column: Column, other_column: Column) -> Join:
#         return Join(self, other, column, other_column)
#
#     def __getitem__(self, key: ColumnLike | Iterable[ColumnLike]) -> Column | ColumnSet | None:
#         if isinstance(key, Iterable):
#             return ColumnSet(
#                 base=self,
#                 columns=[column for column in self._columns if column in key]
#             )
#         return next((column for column in self._columns if column == key), None)
#
#     def __repr__(self):
#         return f'ColumnSet({self._base}, {self._columns}, {self._expressions})'
#
#
# class Table(ColumnSet):
#     def __init__(self, database: Database, name: str):
#         super().__init__()
#         self._database = database
#         self._name = name
#         self._primary_key = None
#         self._foreign_keys = list[Column]()
#         self._constraints = list[Constraint]()
#         self._sequences = list[Sequence]()
#
#     @property
#     def database(self) -> Database:
#         return self._database
#
#     @property
#     def name(self) -> str:
#         return f'{self._database.name}.{self._name}'
#
#     @property
#     def columns(self) -> List[Column]:
#         return self._columns
#
#     @property
#     def primary_key(self) -> Optional[Column]:
#         return self._primary_key
#
#     @primary_key.setter
#     def primary_key(self, primary_key: Column):
#         if self._primary_key is not None:
#             raise ValueError(f'Primary key already exists')
#         self._primary_key = primary_key
#
#     @property
#     def foreign_keys(self) -> List[Column]:
#         return self._foreign_keys
#
#     @property
#     def constraints(self) -> List[Constraint]:
#         return self._constraints
#
#     @property
#     def sequences(self) -> List[Sequence]:
#         return self._sequences
#
#     def add_column[T](self, name: str, base_type: Type[T]) -> Column[T]:
#         column = Column[T](self, name, base_type)
#         self._columns.append(column)
#         setattr(self, name, column)
#         return column
#
#     def validate_record(self, record: Record, statement_type: str):
#         for constraint in self.constraints:
#             constraint.validate(record, statement_type)
#
#     def insert(self, record: RecordLike) -> InsertStatement:
#         return InsertStatement(self, record)
#
#     def insert_one(self, record: RecordLike):
#         return InsertStatement(self, record).execute()
#
#     def __eq__(self, other: object) -> bool:
#         if not isinstance(other, Table):
#             return False
#         return self.name == other.name
#
#     def __hash__(self) -> int:
#         return hash(self.name)
#
#     def __repr__(self):
#         return f'Table({self._database}, \'{self._name}\'))'
#
#
# class Join(ColumnSet):
#     def __init__(self, left: ColumnSet, right: ColumnSet, left_column: Column, right_column: Column):
#         super().__init__(columns=left.columns + right.columns)
#         self._left = left
#         self._right = right
#         self._left_column = left_column
#         self._right_column = right_column
#
#     @property
#     def left(self) -> ColumnSet:
#         return self._left
#
#     @property
#     def right(self) -> ColumnSet:
#         return self._right
#
#     @property
#     def left_column(self) -> Column:
#         return self._left_column
#
#     @property
#     def right_column(self) -> Column:
#         return self._right_column
#
#     def __repr__(self):
#         return f'Join({self._left}, {self._right}, {self._left_column}, {self._right_column}))'
#
#
# class Named(ABC):
#     @property
#     @abstractmethod
#     def name(self) -> str:
#         return NotImplemented
#
#
# class Column[T]:
#     def __init__(self, table: Optional[Table], name: str, base_type: Type[T]):
#         self._table = table
#         self._name = name
#         self._type = base_type
#         self._primary_key_constraint = None
#         self._foreign_key_constraint = None
#         self._sequence = None
#         NotNoneConstraint(self)
#
#     @property
#     def table(self) -> Optional[Table]:
#         return self._table
#
#     @property
#     def name(self) -> str:
#         return f'{self._table.name}.{self._name}' if self._table is not None else self._name
#
#     @property
#     def type(self) -> Type[T]:
#         return self._type
#
#     @property
#     def is_primary_key(self) -> bool:
#         return self._primary_key_constraint is not None
#
#     @property
#     def is_foreign_key(self) -> bool:
#         return self._foreign_key_constraint is not None
#
#     @property
#     def referenced_table(self) -> Optional[Table]:
#         return self._foreign_key_constraint.referenced_table if self.is_foreign_key else None
#
#     @property
#     def sequence(self) -> Optional[Sequence[T]]:
#         return self._sequence
#
#     def primary_key(self) -> Self:
#         self._primary_key_constraint = PrimaryKeyConstraint(self)
#         self._sequence = Sequence.for_column(self)
#         return self
#
#     def foreign_key(self, references: Table) -> Self:
#         self._foreign_key_constraint = ForeignKeyConstraint(self, references)
#         return self
#
#     def eq(self, other: Column[T] | T) -> BoolExpression:
#         return EqualExpression(self, other)
#
#     def ne(self, other: Column[T] | T) -> BoolExpression:
#         return NotEqualExpression(self, other)
#
#     def lt(self, other: Column[T] | T) -> BoolExpression:
#         return LessThanExpression(self, other)
#
#     def le(self, other: Column[T] | T) -> BoolExpression:
#         return LessEqualExpression(self, other)
#
#     def gt(self, other: Column[T] | T) -> BoolExpression:
#         return GreaterThanExpression(self, other)
#
#     def ge(self, other: Column[T] | T) -> BoolExpression:
#         return GreaterEqualExpression(self, other)
#
#     def add(self, other: Column[T] | T) -> Expression[T]:
#         return AddExpression(self, other)
#
#     def sub(self, other: Column[T] | T) -> Expression[T]:
#         return SubExpression(self, other)
#
#     def mul(self, other: Column[T] | T) -> Expression[T]:
#         return MulExpression(self, other)
#
#     def truediv(self, other: Column[T] | T) -> Expression[T]:
#         return TrueDivExpression(self, other)
#
#     def floordiv(self, other: Column[T] | T) -> Expression[T]:
#         return FloorDivExpression(self, other)
#
#     def mod(self, other: Column[T] | T) -> Expression[T]:
#         return ModExpression(self, other)
#
#     def __eq__(self, other: object) -> bool:
#         if not isinstance(other, Column):
#             return False
#         return self.name == other.name
#
#     def __hash__(self) -> int:
#         return hash(self.name)
#
#     def __repr__(self):
#         return f'Column({self._table}, \'{self._name}\', {self._type})'
#
#
# class Constraint(ABC):
#     def __init__(self, column: Column):
#         self._table = column.table
#         self._column = column
#         self._table.constraints.append(self)
#
#     @abstractmethod
#     def validate(self, record: Record, statement_type: str):
#         return NotImplemented
#
#
# class NotNoneConstraint(Constraint):
#     def validate(self, record: Record, statement_type: str):
#         if statement_type != 'INSERT':
#             return
#
#         if self._column != self._table.primary_key and (self._column not in record or record[self._column] is None):
#             raise ValueError(f'{self._column.name} is None')
#
#
# class PrimaryKeyConstraint(Constraint):
#     def __init__(self, column: Column):
#         super().__init__(column)
#         self._table._primary_key = column
#
#     def validate(self, record: Record, statement_type: str):
#         if statement_type != 'INSERT':
#             return
#
#         pass
#
#
# class ForeignKeyConstraint(Constraint):
#     def __init__(self, column: Column, referenced_table: Table):
#         super().__init__(column)
#
#         if referenced_table.primary_key is None:
#             raise ValueError(f'Referenced table does not have primary key')
#
#         self._referenced_table = referenced_table
#         self._table.foreign_keys.append(column)
#
#     def validate(self, record: Record, statement_type: str):
#         pass
#
#
# class Sequence[T]:
#     def __init__(self, column: Column[T]):
#         self._table = column.table
#         self._column = column
#         self._table.sequences.append(self)
#
#     @classmethod
#     def for_column[U](cls, column: Column[U]) -> Sequence[U]:
#         return {
#             int: IntSequence(column),
#             float: FloatSequence(column),
#             str: StrSequence(column)
#         }[column.type]
#
#     @abstractmethod
#     def __next__(self) -> T:
#         return NotImplemented
#
#
# class IntSequence(Sequence[int]):
#     def __init__(self, column: Column[int]):
#         super().__init__(column)
#         self._value = 1
#
#     def __next__(self) -> int:
#         value = self._value
#         self._value += 1
#         return value
#
#
# class FloatSequence(Sequence[float]):
#     def __init__(self, column: Column[float]):
#         super().__init__(column)
#         self._value = 1.0
#
#     def __next__(self) -> float:
#         value = self._value
#         self._value += 1.0
#         return value
#
#
# class StrSequence(Sequence[str]):
#     def __next__(self) -> str:
#         return str(uuid.uuid4())
#
#
# class Record(Dict[str, Any]):
#     def __init__(self, *args: Any, **kwargs: Any):
#         super().__init__()
#         self.update(*args, **kwargs)
#
#     def __getitem__(self, key: ColumnLike | Iterable[ColumnLike]) -> Any:
#         if isinstance(key, Iterable):
#             key = set(item.name if isinstance(item, Column) else item for item in key)
#             return Record({k: v for k, v in self.items() if k in key})
#         return super().__getitem__(self._normalize_key(key))
#
#     def __setitem__(self, key: ColumnLike, value: Any) -> None:
#         super().__setitem__(self._normalize_key(key), value)
#
#     def __delitem__(self, key: ColumnLike) -> None:
#         super().__delitem__(self._normalize_key(key))
#
#     def __contains__(self, key: object) -> bool:
#         if not isinstance(key, (str, Column)):
#             return False
#         return super().__contains__(self._normalize_key(key))
#
#     def get(self, key: ColumnLike, default: Any = None) -> Any:
#         return super().get(self._normalize_key(key), default)
#
#     def pop(self, key: ColumnLike, *args: Any) -> Any:
#         return super().pop(self._normalize_key(key), *args)
#
#     def setdefault(self, key: ColumnLike, default: Any = None) -> Any:
#         return super().setdefault(self._normalize_key(key), default)
#
#     def update(self, other: Any = (), /, **kwargs: Any) -> None:
#         if isinstance(other, Mapping):
#             for k in other:
#                 self[self._normalize_key(k)] = other[k]
#         else:
#             for k, v in other:
#                 self[self._normalize_key(k)] = v
#         for k, v in kwargs.items():
#             self[self._normalize_key(k)] = v
#
#     def _normalize_key(self, key: ColumnLike) -> str:
#         if isinstance(key, str):
#             return key
#         elif isinstance(key, Column):
#             return key.name
#         elif isinstance(key, Expression):
#             return key.name
#         elif isinstance(key, Aggregation):
#             return key.name
#         else:
#             raise TypeError('Key must be str or Column')
#
#
# class Expression[T](ABC):
#     @abstractmethod
#     def evaluate(self, record: Record) -> T:
#         return NotImplemented
#
#     @property
#     @abstractmethod
#     def columns(self) -> List[Column]:
#         return NotImplemented
#
#     @classmethod
#     def const[T](cls, const: T) -> ConstExpression[T]:
#         return ConstExpression(const)
#
#     @classmethod
#     def true(cls) -> BoolExpression:
#         return TrueExpression()
#
#     @classmethod
#     def false(cls) -> BoolExpression:
#         return FalseExpression()
#
#     def eq(self, other: Expression[T] | Column[T] | T) -> BoolExpression:
#         return EqualExpression(self, other)
#
#     def ne(self, other: Expression[T] | Column[T] | T) -> BoolExpression:
#         return NotEqualExpression(self, other)
#
#     def lt(self, other: Expression[T] | Column[T] | T) -> BoolExpression:
#         return LessThanExpression(self, other)
#
#     def le(self, other: Expression[T] | Column[T] | T) -> BoolExpression:
#         return LessEqualExpression(self, other)
#
#     def gt(self, other: Expression[T] | Column[T] | T) -> BoolExpression:
#         return GreaterThanExpression(self, other)
#
#     def ge(self, other: Expression[T] | Column[T] | T) -> BoolExpression:
#         return GreaterEqualExpression(self, other)
#
#     def add(self, other: Expression[T] | Column[T] | T) -> Expression[T]:
#         return AddExpression(self, other)
#
#     def sub(self, other: Expression[T] | Column[T] | T) -> Expression[T]:
#         return SubExpression(self, other)
#
#     def mul(self, other: Expression[T] | Column[T] | T) -> Expression[T]:
#         return MulExpression(self, other)
#
#     def truediv(self, other: Expression[T] | Column[T] | T) -> Expression[T]:
#         return TrueDivExpression(self, other)
#
#     def floordiv(self, other: Expression[T] | Column[T] | T) -> Expression[T]:
#         return FloorDivExpression(self, other)
#
#     def mod(self, other: Expression[T] | Column[T] | T) -> Expression[T]:
#         return ModExpression(self, other)
#
#
# class ConstExpression[T](Expression[T]):
#     def __init__(self, value: T):
#         self._value = value
#
#     def evaluate(self, record: Record) -> T:
#         return self._value
#
#     @property
#     def name(self) -> str:
#         return str(self._value)
#
#     @property
#     def columns(self) -> list[Column]:
#         return []
#
#
# class ColumnExpression[T](Expression[T]):
#     def __init__(self, column: Column[T]):
#         self._column = column
#
#     def evaluate(self, record: Record) -> T:
#         return record[self._column]
#
#     @property
#     def name(self) -> str:
#         return self._column.name
#
#     @property
#     def columns(self) -> list[Column]:
#         return [self._column]
#
#
# class UnaryExpression[T, U](Expression[U], ABC):
#     def __init__(self, value: Expression[T] | Column[T] | T):
#         self._value = self._wrap(value)
#
#     def _wrap(self, value: Expression[T] | Column[T] | T) -> Expression[T]:
#         if isinstance(value, Expression):
#             return value
#         if isinstance(value, Column):
#             return ColumnExpression(value)
#         return ConstExpression(value)
#
#     @property
#     def columns(self) -> list[Column]:
#         return self._value.columns
#
#
# class BinaryExpression[T, U](UnaryExpression[T, U], ABC):
#     def __init__(self, value: Expression[T] | T, other: Expression[T] | T):
#         super().__init__(value)
#         self._other = self._wrap(other)
#
#     @property
#     def columns(self) -> list[Column]:
#         return list(set(self._value.columns) | set(self._other.columns))
#
#
# class BoolExpression(Expression[bool], ABC):
#     @abstractmethod
#     def evaluate(self, record: Record) -> bool:
#         return NotImplemented
#
#     def not_(self) -> BoolExpression:
#         return NotExpression(self)
#
#     def and_(self, other: BoolExpression) -> BoolExpression:
#         return AndExpression(self, other)
#
#     def or_(self, other: BoolExpression) -> BoolExpression:
#         return OrExpression(self, other)
#
#
# class UnaryBoolExpression(UnaryExpression[bool, bool], BoolExpression, ABC):
#     pass
#
#
# class NotExpression(UnaryBoolExpression):
#     def evaluate(self, record: Record) -> bool:
#         return not self._value.evaluate(record)
#
#     @property
#     def name(self) -> str:
#         return f'not ({self._value.name})'
#
#
# class BinaryBoolExpression(BinaryExpression[bool, bool], BoolExpression, ABC):
#     pass
#
#
# class FalseExpression(ConstExpression[bool], BoolExpression):
#     def __init__(self):
#         super().__init__(False)
#
#
# class TrueExpression(ConstExpression[bool], BoolExpression):
#     def __init__(self):
#         super().__init__(True)
#
#
# class AndExpression(BinaryBoolExpression):
#     def evaluate(self, record: Record) -> bool:
#         return self._value.evaluate(record) and self._other.evaluate(record)
#
#     @property
#     def name(self) -> str:
#         return f'({self._value.name}) and ({self._other.name})'
#
#
# class OrExpression(BinaryBoolExpression):
#     def evaluate(self, record: Record) -> bool:
#         return self._value.evaluate(record) or self._other.evaluate(record)
#
#     @property
#     def name(self) -> str:
#         return f'({self._value.name}) or ({self._other.name})'
#
#
# class ComparisonExpression[T](BinaryExpression[T, bool], BoolExpression, ABC):
#     pass
#
#
# class EqualExpression(ComparisonExpression):
#     def evaluate(self, record: Record) -> bool:
#         return self._value.evaluate(record) == self._other.evaluate(record)
#
#     @property
#     def name(self) -> str:
#         return f'({self._value.name}) == ({self._other.name})'
#
#
# class NotEqualExpression(ComparisonExpression):
#     def evaluate(self, record: Record) -> bool:
#         return self._value.evaluate(record) != self._other.evaluate(record)
#
#     @property
#     def name(self) -> str:
#         return f'({self._value.name}) != ({self._other.name})'
#
#
# class LessThanExpression(ComparisonExpression):
#     def evaluate(self, record: Record) -> bool:
#         return self._value.evaluate(record) < self._other.evaluate(record)
#
#     @property
#     def name(self) -> str:
#         return f'({self._value.name}) < ({self._other.name})'
#
#
# class GreaterThanExpression(ComparisonExpression):
#     def evaluate(self, record: Record) -> bool:
#         return self._value.evaluate(record) > self._other.evaluate(record)
#
#     @property
#     def name(self) -> str:
#         return f'({self._value.name}) > ({self._other.name})'
#
#
# class LessEqualExpression(ComparisonExpression):
#     def evaluate(self, record: Record) -> bool:
#         return self._value.evaluate(record) <= self._other.evaluate(record)
#
#     @property
#     def name(self) -> str:
#         return f'({self._value.name}) <= ({self._other.name})'
#
#
# class GreaterEqualExpression(ComparisonExpression):
#     def evaluate(self, record: Record) -> bool:
#         return self._value.evaluate(record) >= self._other.evaluate(record)
#
#     @property
#     def name(self) -> str:
#         return f'({self._value.name}) >= ({self._other.name})'
#
#
# class ArithmeticExpression[T](BinaryExpression[T, T], ABC):
#     pass
#
#
# class AddExpression[T](ArithmeticExpression[T]):
#     def evaluate(self, record: Record) -> T:
#         return self._value.evaluate(record) + self._other.evaluate(record)
#
#     @property
#     def name(self) -> str:
#         return f'({self._value.name}) + ({self._other.name})'
#
#
# class SubExpression[T](ArithmeticExpression[T]):
#     def evaluate(self, record: Record) -> T:
#         return self._value.evaluate(record) - self._other.evaluate(record)
#
#     @property
#     def name(self) -> str:
#         return f'({self._value.name}) - ({self._other.name})'
#
#
# class MulExpression[T](ArithmeticExpression[T]):
#     def evaluate(self, record: Record) -> T:
#         return self._value.evaluate(record) * self._other.evaluate(record)
#
#     @property
#     def name(self) -> str:
#         return f'({self._value.name}) * ({self._other.name})'
#
#
# class TrueDivExpression[T](ArithmeticExpression[T]):
#     def evaluate(self, record: Record) -> T:
#         return self._value.evaluate(record) / self._other.evaluate(record)
#
#     @property
#     def name(self) -> str:
#         return f'({self._value.name}) / ({self._other.name})'
#
#
# class FloorDivExpression[T](ArithmeticExpression[T]):
#     def evaluate(self, record: Record) -> T:
#         return self._value.evaluate(record) // self._other.evaluate(record)
#
#     @property
#     def name(self) -> str:
#         return f'({self._value.name}) // ({self._other.name})'
#
#
# class ModExpression[T](ArithmeticExpression[T]):
#     def evaluate(self, record: Record) -> T:
#         return self._value.evaluate(record) % self._other.evaluate(record)
#
#     @property
#     def name(self) -> str:
#         return f'({self._value.name}) % ({self._other.name})'
#
#
# class Aggregation[T, U](ABC):
#     def __init__(self, expression: Column[T] | Expression[T]):
#         self._expression = expression if isinstance(expression, Expression) else ColumnExpression(expression)
#
#     @classmethod
#     def sum(cls, expression: Column[T] | Expression[T]) -> SumAggregation[T]:
#         return SumAggregation[T](expression)
#
#     @classmethod
#     def count(cls, expression: Column[T] | Expression[T]) -> CountAggregation[T]:
#         return CountAggregation[T](expression)
#
#     @classmethod
#     def list(cls, expression: Column[T] | Expression[T]) -> ListAggregation[T]:
#         return ListAggregation[T](expression)
#
#     @abstractmethod
#     def evaluate(self, records: List[Record]) -> U:
#         return NotImplemented
#
#     @property
#     def columns(self) -> List[Column]:
#         return self._expression.columns
#
#
# class SumAggregation[T](Aggregation[T, T]):
#     def evaluate(self, records: List[Record]) -> T:
#         return sum(self._expression.evaluate(record) for record in records)
#
#     @property
#     def name(self) -> str:
#         return f'sum({self._expression.name})'
#
#
# class CountAggregation[T](Aggregation[T, int]):
#     def evaluate(self, records: List[Record]) -> int:
#         return len(records)
#
#     @property
#     def name(self) -> str:
#         return f'count({self._expression.name})'
#
#
# class ListAggregation[T](Aggregation[T, List[T]]):
#     def evaluate(self, records: List[Record]) -> List[T]:
#         return [self._expression.evaluate(record) for record in records]
#
#     @property
#     def name(self) -> str:
#         return f'list({self._expression.name})'
#
#
# class Page:
#     def __init__(self, number: int):
#         self._number = number
#         self._records = list[Record]()
#         self._size = 0
#
#     @property
#     def number(self) -> int:
#         return self._number
#
#     @property
#     def records(self) -> List[Record]:
#         return self._records
#
#     @records.setter
#     def records(self, records: List[Record]):
#         self._records = records
#
#     @property
#     def size(self) -> int:
#         return self._size
#
#     @size.setter
#     def size(self, size: int):
#         self._size = size
#
#
# storage = dict[str, List[Page]]()
#
#
# class ScanStrategy(ABC):
#     @abstractmethod
#     def scan(self, column_set: ColumnSet) -> List[Record]:
#         return NotImplemented
#
#
# class SequentialScan(ScanStrategy):
#     def scan(self, column_set: ColumnSet) -> List[Record]:
#         tables = column_set.tables
#         if len(tables) != 1:
#             raise ValueError(f'Not a table')
#         table = tables.pop()
#
#         columns_to_include = set(column_set.columns).union([table.primary_key]).union(table.foreign_keys)
#         return [record[columns_to_include] for record in storage[table.name]]
#
#
# class JoinStrategy(ABC):
#     @abstractmethod
#     def join(
#             self,
#             left: ColumnSet,
#             right: ColumnSet,
#             left_column: Column,
#             right_column: Column,
#             left_records: List[Record],
#             right_records: List[Record]
#     ) -> List[Record]:
#         return NotImplemented
#
#
# class HashJoin(JoinStrategy):
#     def join(
#             self,
#             left: ColumnSet,
#             right: ColumnSet,
#             left_column: Column,
#             right_column: Column,
#             left_records: List[Record],
#             right_records: List[Record]
#     ) -> List[Record]:
#         hash_table = {right_record[right_column]: list[Record]() for right_record in right_records}
#
#         for right_record in right_records:
#             value = right_record[right_column]
#             hash_table[value].append(right_record)
#
#         result = list[Record]()
#         for left_record in left_records:
#             value = left_record[left_column]
#             if value in hash_table:
#                 for right_record in hash_table[value]:
#                     merged_record = Record({**left_record, **right_record})
#                     result.append(merged_record)
#
#         return result
#
#
# type ColumnLike = Column | Expression | Aggregation | str
# type RecordLike = Record | Dict[ColumnLike, Any]
#
#
# class Statement[T](ABC):
#     @abstractmethod
#     def execute(self) -> T:
#         return NotImplemented
#
#     @property
#     @abstractmethod
#     def type(self) -> str:
#         return NotImplemented
#
#
# class SelectStatement(Statement[List[Record]]):
#     def __init__(self, column_set: ColumnSet):
#         self._column_set = column_set
#         self._where_clause: Optional[BoolExpression] = None
#         self._order_by_clause: Optional[Expression] = None
#         self._group_by_clause: Optional[Expression] = None
#         self._reverse_order = False
#
#     def where(self, where_clause: BoolExpression) -> Self:
#         self._where_clause = where_clause if self._where_clause is None else self._where_clause.and_(where_clause)
#         return self
#
#     def order_by(self, order_by_clause: Column | Expression, reverse: bool = False) -> Self:
#         if isinstance(order_by_clause, Expression):
#             self._order_by_clause = order_by_clause
#         else:
#             self._order_by_clause = ColumnExpression(order_by_clause)
#         self._reverse_order = reverse
#         return self
#
#     def group_by(self, group_by_clause: Column | Expression) -> Self:
#         if isinstance(group_by_clause, Expression):
#             self._group_by_clause = group_by_clause
#         else:
#             self._group_by_clause = ColumnExpression(group_by_clause)
#         return self
#
#     def execute(self) -> List[Record]:
#         records = self._join(self._column_set)
#         return self._post_process(records)
#
#     @property
#     def type(self) -> str:
#         return 'SELECT'
#
#     def _scan(self, column_set: ColumnSet) -> List[Record]:
#         tables = column_set.tables
#
#         if len(tables) > 1:
#             raise ValueError(f'Multiple tables without join: {tables}')
#         elif len(tables) < 1:
#             raise ValueError('No tables')
#
#         scan_strategy = self._get_scan_strategy(column_set)
#
#         return scan_strategy.scan(column_set)
#
#     def _join(self, column_set: ColumnSet) -> List[Record]:
#         join: Join = self._get_join(column_set)
#
#         if join is None:
#             return self._scan(column_set)
#
#         join_strategy = self._get_join_strategy(column_set)
#
#         left = join.left
#         right = join.right
#         left_column = join.left_column
#         right_column = join.right_column
#         left_records = self._join(left)
#         right_records = self._join(right)
#
#         records = join_strategy.join(left, right, left_column, right_column, left_records, right_records)
#
#         return records
#
#     def _get_join(self, column_set: ColumnSet) -> Optional[Join]:
#         if isinstance(column_set, Join):
#             return column_set
#
#         if column_set.base is None:
#             return None
#
#         return self._get_join(column_set.base)
#
#     def _get_scan_strategy(self, column_set: ColumnSet) -> ScanStrategy:
#         return SequentialScan()
#
#     def _get_join_strategy(self, column_set: ColumnSet) -> JoinStrategy:
#         return HashJoin()
#
#     def _post_process(self, records: List[Record]) -> List[Record]:
#         records = self._evaluate_expressions(records)
#         records = self._group_by(records)
#         records = self._filter(records)
#         records = self._order_by(records)
#         return records
#
#     def _group_by(self, records: List[Record]) -> List[Record]:
#         if self._group_by_clause is None:
#             return records
#
#         grouped_records = {self._group_by_clause.evaluate(record): list[Record]() for record in records}
#         for record in records:
#             grouped_records[self._group_by_clause.evaluate(record)].append(record)
#
#         records_after_grouping = list[Record]()
#         for k, v in grouped_records.items():
#             record = Record({self._group_by_clause: k})
#             for aggregation in self._column_set.aggregations:
#                 record[aggregation] = aggregation.evaluate(v)
#             records_after_grouping.append(record)
#
#         return records_after_grouping
#
#     def _filter(self, records: List[Record]) -> List[Record]:
#         if self._where_clause is None:
#             return records
#         return [record for record in records if self._where_clause.evaluate(record)]
#
#     def _remove_columns(self, records: List[Record]) -> List[Record]:
#         return [record[self._column_set.columns] for record in records]
#
#     def _evaluate_expressions(self, records: List[Record]) -> List[Record]:
#         for record in records:
#             for expression in self._column_set.expressions:
#                 record[expression.name] = expression.evaluate(record)
#         return records
#
#     def _order_by(self, records: List[Record]) -> List[Record]:
#         if self._order_by_clause is None:
#             return records
#         return sorted(records, key=lambda record: self._order_by_clause.evaluate(record), reverse=self._reverse_order)
#
#
# class InsertStatement(Statement[None]):
#     def __init__(self, table: Table, record: RecordLike):
#         self._table = table
#         self._records = list[Record]()
#         self.insert(record)
#
#     def insert(self, record: RecordLike) -> Self:
#         self._records.append(record if isinstance(record, Record) else Record(record))
#         return self
#
#     def execute(self) -> None:
#         for record in self._records:
#             self._table.validate_record(record, self.type)
#
#         if self._table.primary_key and not self._table.primary_key in record:
#             record[self._table.primary_key] = next(self._table.primary_key.sequence)
#
#         if self._table.name not in storage:
#             storage[self._table.name] = []
#
#         storage[self._table.name].extend(self._records)
#
#     @property
#     def type(self) -> str:
#         return 'INSERT'
