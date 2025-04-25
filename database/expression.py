from abc import ABC, abstractmethod
from typing import Any, Callable, Optional

from database.aliasmixin import AliasMixin


def expression(expr):
    if isinstance(expr, Expression):
        return expr
    else:
        return ConstantExpression(expr)


class Expression[T](AliasMixin, ABC):
    def __init__(self):
        self._compiled: Optional[Callable[[Record], T]] = None

    def evaluate(self, record: 'Record') -> T:
        if self._compiled is None:
            return self._evaluate(record)
        else:
            return self._compiled(record)

    @abstractmethod
    def _evaluate(self, record: 'Record') -> T:
        return NotImplemented

    def compile(self) -> Callable[['Record'], T]:
        if self._compiled is None:
            self._compiled = self._compile()
        return self._compiled

    @abstractmethod
    def _compile(self) -> Callable[['Record'], T]:
        return NotImplemented

    @classmethod
    def raw(cls, name: str):
        return RawExpression(name)

    @classmethod
    def constant[U](cls, value: U):
        return ConstantExpression(value)

    @classmethod
    def function[T, U](cls, func: Callable[[T], U]):
        return lambda expression: FunctionExpression(expression, func)

    def __add__(self, other):
        return AddExpression(self, other)

    def __radd__(self, other):
        return expression(other) + self

    def __sub__(self, other):
        return SubExpression(self, other)

    def __rsub__(self, other):
        return expression(other) - self

    def __mul__(self, other):
        return MulExpression(self, other)

    def __rmul__(self, other):
        return expression(other) * self

    def __truediv__(self, other):
        return TrueDivExpression(self, other)

    def __rtruediv__(self, other):
        return expression(other) / self

    def __floordiv__(self, other):
        return FloorDivExpression(self, other)

    def __rfloordiv__(self, other):
        return expression(other) // self

    def __mod__(self, other):
        return ModExpression(self, other)

    def __rmod__(self, other):
        return expression(other) % self

    def __pow__(self, other):
        return PowExpression(self, other)

    def __rpow__(self, other):
        return expression(other) ** self

    def __lt__(self, other):
        return LessThanExpression(self, other)

    def __le__(self, other):
        return LessEqualExpression(self, other)

    def __eq__(self, other):
        return EqualExpression(self, other)

    def __ne__(self, other):
        return NotEqualExpression(self, other)

    def __gt__(self, other):
        return GreaterThanExpression(self, other)

    def __ge__(self, other):
        return GreaterEqualExpression(self, other)

    def __neg__(self):
        return NegExpression(self)

    def __pos__(self):
        return PosExpression(self)

    def __invert__(self):
        return InvertExpression(self)

    def __hash__(self):
        return hash(self.name)

    def __repr__(self):
        return self.name


class ConstantExpression[T](Expression[T]):
    def __init__(self, value: T):
        super().__init__()
        self._value = value

    def _evaluate(self, record: 'Record') -> T:
        return self._value

    def _compile(self) -> Callable[['Record'], T]:
        return lambda record: self._value

    def _get_name(self):
        return str(self._value)


class RawExpression[T](Expression[T]):
    def __init__(self, name: str):
        super().__init__()
        self._name = name

    def _evaluate(self, record: 'Record') -> T:
        return record[self._name]

    def _compile(self) -> Callable[['Record'], T]:
        return lambda record: record[self._name]

    def _get_name(self):
        return self._name


class UnaryExpression[T](Expression[T], ABC):
    def __init__(self, operand: Expression[Any]):
        super().__init__()
        self._operand = operand


class FunctionExpression[T, U](UnaryExpression[U]):
    def __init__(self, operand: Expression[T], function: Callable[[T], U]):
        super().__init__(operand)
        self._function = function

    def _evaluate(self, record: 'Record') -> U:
        return self._function(self._operand.evaluate(record))

    def _compile(self) -> Callable[['Record'], U]:
        compiled_operand = self._operand.compile()
        return lambda record: self._function(compiled_operand(record))

    def _get_name(self):
        return f'f{str(abs(hash(self._function)))[:3]}({self._operand.name})'


class NegExpression[T](UnaryExpression[T]):
    def _evaluate(self, record: 'Record') -> T:
        return -self._operand.evaluate(record)

    def _compile(self) -> Callable[['Record'], T]:
        compiled_operand = self._operand.compile()
        return lambda record: -compiled_operand(record)

    def _get_name(self):
        return f'-{self._operand.name}'


class PosExpression[T](UnaryExpression[T]):
    def _evaluate(self, record: 'Record') -> T:
        return +self._operand.evaluate(record)

    def _compile(self) -> Callable[['Record'], T]:
        compiled_operand = self._operand.compile()
        return lambda record: +compiled_operand(record)

    def _get_name(self):
        return f'+{self._operand.name}'


class InvertExpression[T](UnaryExpression[T]):
    def _evaluate(self, record: 'Record') -> T:
        return ~self._operand.evaluate(record)

    def _compile(self) -> Callable[['Record'], T]:
        compiled_operand = self._operand.compile()
        return lambda record: ~compiled_operand(record)

    def _get_name(self):
        return f'~{self._operand.name}'


class BinaryExpression[T](Expression[T], ABC):
    def __init__(self, left: T | Expression[T], right: T | Expression[T]):
        super().__init__()
        self._left = left if isinstance(left, Expression) else expression(left)
        self._right = right if isinstance(right, Expression) else expression(right)


class AddExpression[T](BinaryExpression[T]):
    def _evaluate(self, record: 'Record') -> T:
        return self._left.evaluate(record) + self._right.evaluate(record)

    def _compile(self) -> Callable[['Record'], T]:
        compiled_left = self._left.compile()
        compiled_right = self._right.compile()
        return lambda record: compiled_left(record) + compiled_right(record)

    def _get_name(self):
        return f'({self._left.name} + {self._right.name})'


class SubExpression[T](BinaryExpression[T]):
    def _evaluate(self, record: 'Record') -> T:
        return self._left.evaluate(record) - self._right.evaluate(record)

    def _compile(self) -> Callable[['Record'], T]:
        compiled_left = self._left.compile()
        compiled_right = self._right.compile()
        return lambda record: compiled_left(record) - compiled_right(record)

    def _get_name(self):
        return f'({self._left.name} - {self._right.name})'


class MulExpression[T](BinaryExpression[T]):
    def _evaluate(self, record: 'Record') -> T:
        return self._left.evaluate(record) * self._right.evaluate(record)

    def _compile(self) -> Callable[['Record'], T]:
        compiled_left = self._left.compile()
        compiled_right = self._right.compile()
        return lambda record: compiled_left(record) * compiled_right(record)

    def _get_name(self):
        return f'({self._left.name} * {self._right.name})'


class TrueDivExpression[T](BinaryExpression[T]):
    def _evaluate(self, record: 'Record') -> T:
        return self._left.evaluate(record) / self._right.evaluate(record)

    def _compile(self) -> Callable[['Record'], T]:
        compiled_left = self._left.compile()
        compiled_right = self._right.compile()
        return lambda record: compiled_left(record) / compiled_right(record)

    def _get_name(self):
        return f'({self._left.name} / {self._right.name})'


class FloorDivExpression[T](BinaryExpression[T]):
    def _evaluate(self, record: 'Record') -> T:
        return self._left.evaluate(record) // self._right.evaluate(record)

    def _compile(self) -> Callable[['Record'], T]:
        compiled_left = self._left.compile()
        compiled_right = self._right.compile()
        return lambda record: compiled_left(record) // compiled_right(record)

    def _get_name(self):
        return f'({self._left.name} // {self._right.name})'


class ModExpression[T](BinaryExpression[T]):
    def _evaluate(self, record: 'Record') -> T:
        return self._left.evaluate(record) % self._right.evaluate(record)

    def _compile(self) -> Callable[['Record'], T]:
        compiled_left = self._left.compile()
        compiled_right = self._right.compile()
        return lambda record: compiled_left(record) % compiled_right(record)

    def _get_name(self):
        return f'({self._left.name} % {self._right.name})'


class PowExpression[T](BinaryExpression[T]):
    def _evaluate(self, record: 'Record') -> T:
        return self._left.evaluate(record) ** self._right.evaluate(record)

    def _compile(self) -> Callable[['Record'], T]:
        compiled_left = self._left.compile()
        compiled_right = self._right.compile()
        return lambda record: compiled_left(record) ** compiled_right(record)

    def _get_name(self):
        return f'({self._left.name} ** {self._right.name})'


class BoolExpression(Expression[bool], ABC):
    def __and__(self, other):
        return AndExpression(self, other)

    def __rand__(self, other):
        return AndExpression(ConstantExpression(other), self)

    def __or__(self, other):
        return OrExpression(self, other)

    def __ror__(self, other):
        return OrExpression(ConstantExpression(other), self)

    def __xor__(self, other):
        return XorExpression(self, other)

    def __rxor__(self, other):
        return XorExpression(ConstantExpression(other), self)

    def __invert__(self):
        return NotExpression(self)


class AndExpression(BoolExpression, BinaryExpression[bool]):
    def _evaluate(self, record: 'Record') -> bool:
        return self._left.evaluate(record) and self._right.evaluate(record)

    def _compile(self) -> Callable[['Record'], bool]:
        compiled_left = self._left.compile()
        compiled_right = self._right.compile()
        return lambda record: compiled_left(record) and compiled_right(record)

    def _get_name(self):
        return f"({self._left.name} & {self._right.name})"


class OrExpression(BoolExpression, BinaryExpression[bool]):
    def _evaluate(self, record: 'Record') -> bool:
        return self._left.evaluate(record) or self._right.evaluate(record)

    def _compile(self) -> Callable[['Record'], bool]:
        compiled_left = self._left.compile()
        compiled_right = self._right.compile()
        return lambda record: compiled_left(record) or compiled_right(record)

    def _get_name(self):
        return f"({self._left.name} | {self._right.name})"


class XorExpression(BoolExpression, BinaryExpression[bool]):
    def _evaluate(self, record: 'Record') -> bool:
        return bool(self._left.evaluate(record)) ^ bool(self._right.evaluate(record))

    def _compile(self) -> Callable[['Record'], bool]:
        compiled_left = self._left.compile()
        compiled_right = self._right.compile()
        return lambda record: bool(compiled_left(record)) ^ bool(compiled_right(record))

    def _get_name(self):
        return f"({self._left.name} ^ {self._right.name})"


class NotExpression(BoolExpression, UnaryExpression[bool]):
    def _evaluate(self, record: 'Record') -> bool:
        return not self._operand.evaluate(record)

    def _compile(self) -> Callable[['Record'], bool]:
        compiled_operand = self._operand.compile()
        return lambda record: not compiled_operand(record)

    def _get_name(self):
        return f"~{self._operand.name}"


class LessThanExpression(BoolExpression, BinaryExpression[bool]):
    def _evaluate(self, record: 'Record') -> bool:
        return self._left.evaluate(record) < self._right.evaluate(record)

    def _compile(self) -> Callable[['Record'], bool]:
        compiled_left = self._left.compile()
        compiled_right = self._right.compile()
        return lambda record: compiled_left(record) < compiled_right(record)

    def _get_name(self):
        return f'({self._left.name} < {self._right.name})'


class LessEqualExpression(BoolExpression, BinaryExpression[bool]):
    def _evaluate(self, record: 'Record') -> bool:
        return self._left.evaluate(record) <= self._right.evaluate(record)

    def _compile(self) -> Callable[['Record'], bool]:
        compiled_left = self._left.compile()
        compiled_right = self._right.compile()
        return lambda record: compiled_left(record) <= compiled_right(record)

    def _get_name(self):
        return f'({self._left.name} <= {self._right.name})'


class EqualExpression(BoolExpression, BinaryExpression[bool]):
    def _evaluate(self, record: 'Record') -> bool:
        return self._left.evaluate(record) == self._right.evaluate(record)

    def _compile(self) -> Callable[['Record'], bool]:
        compiled_left = self._left.compile()
        compiled_right = self._right.compile()
        return lambda record: compiled_left(record) == compiled_right(record)

    def _get_name(self):
        return f'({self._left.name} == {self._right.name})'


class NotEqualExpression(BoolExpression, BinaryExpression[bool]):
    def _evaluate(self, record: 'Record') -> bool:
        return self._left.evaluate(record) != self._right.evaluate(record)

    def _compile(self) -> Callable[['Record'], bool]:
        compiled_left = self._left.compile()
        compiled_right = self._right.compile()
        return lambda record: compiled_left(record) != compiled_right(record)

    def _get_name(self):
        return f'({self._left.name} != {self._right.name})'


class GreaterThanExpression(BoolExpression, BinaryExpression[bool]):
    def _evaluate(self, record: 'Record') -> bool:
        return self._left.evaluate(record) > self._right.evaluate(record)

    def _compile(self) -> Callable[['Record'], bool]:
        compiled_left = self._left.compile()
        compiled_right = self._right.compile()
        return lambda record: compiled_left(record) > compiled_right(record)

    def _get_name(self):
        return f'({self._left.name} > {self._right.name})'


class GreaterEqualExpression(BoolExpression, BinaryExpression[bool]):
    def _evaluate(self, record: 'Record') -> bool:
        return self._left.evaluate(record) >= self._right.evaluate(record)

    def _compile(self) -> Callable[['Record'], bool]:
        compiled_left = self._left.compile()
        compiled_right = self._right.compile()
        return lambda record: compiled_left(record) >= compiled_right(record)

    def _get_name(self):
        return f'({self._left.name} >= {self._right.name})'


from database.record import Record
