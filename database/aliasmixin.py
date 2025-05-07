import copy
from abc import ABC
from typing import Self, override

from database.namemixin import NameMixin


class AliasMixin(NameMixin, ABC):
    def alias(self, alias: str) -> Self:
        other = copy.copy(self)
        setattr(other, '_alias', alias)
        return other

    @property
    def original_name(self) -> str:
        return self._get_name()

    @override
    @property
    def name(self) -> str:
        alias = getattr(self, '_alias', None)
        return alias if alias is not None else self._get_name()
