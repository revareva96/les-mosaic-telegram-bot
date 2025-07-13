import typing as t

import pytest

from bootstrap.constants import OrderStatus
from infrastructure.dal.abstractions import IOrderRepo


@pytest.fixture
def engine():
    return list()


@pytest.fixture
def fake_order_repo(engine):
    return FakeOrderRepo(engine=engine)


class FakeOrderRepo(IOrderRepo):

    def __init__(self, engine: list):
        self._engine = engine

    async def get_uncompleted_order(self, username: str):
        for d in self._engine:
            if d['username'] == username and d['status'] not in (OrderStatus.ACCEPTED, OrderStatus.CANCELED):
                return d

    async def create_order(self, info: dict[str, t.Any]):
        info['status'] = OrderStatus.CREATED
        self._engine.append(info)

    async def update_order(self, username: str, info: dict[str, t.Any]):
        order = [d for d in self._engine if
                 d['username'] == username and d['status'] not in (OrderStatus.ACCEPTED, OrderStatus.CANCELED)][0]
        order.update(info)
