from abc import ABC, abstractmethod


class NameMixin(ABC):
    @abstractmethod
    def _get_name(self):
        return NotImplemented

    @property
    def name(self) -> str:
        return NotImplemented
