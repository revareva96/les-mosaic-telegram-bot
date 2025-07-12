from abc import ABC, abstractmethod
import typing as t


class IOrderRepo(ABC):

    @abstractmethod
    async def get_uncompleted_order(self, username: str):
        ...

    @abstractmethod
    async def create_order(self, info: dict[str, t.Any]):
        ...

    @abstractmethod
    async def update_order(self, username: str, info: dict[str, t.Any]):
        ...
