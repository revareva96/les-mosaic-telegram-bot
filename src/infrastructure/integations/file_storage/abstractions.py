import abc
import typing as t


class IStorage(abc.ABC):

    @abc.abstractmethod
    def save_photo(self, username: str, file: t.Any) -> str:
        ...
