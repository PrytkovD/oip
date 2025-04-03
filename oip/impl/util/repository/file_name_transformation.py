from abc import ABC, abstractmethod


class FileNameTransformer(ABC):
    @abstractmethod
    def apply_transformation(self, file_name: str) -> str:
        return NotImplemented

    @abstractmethod
    def revert_transformation(self, transformed_file_name: str) -> str:
        return NotImplemented


class NoopFileNameTransformer(FileNameTransformer):
    def apply_transformation(self, file_name: str) -> str:
        return file_name

    def revert_transformation(self, transformed_file_name: str) -> str:
        return transformed_file_name


class PrefixSuffixFileNameTransformer(FileNameTransformer):
    def __init__(self, prefix: str = '', suffix: str = ''):
        self._prefix = prefix
        self._suffix = suffix

    def apply_transformation(self, file_name: str) -> str:
        return f"{self._prefix}{file_name}{self._suffix}"

    def revert_transformation(self, transformed_file_name: str) -> str:
        return transformed_file_name.removeprefix(self._prefix).removesuffix(self._suffix)
