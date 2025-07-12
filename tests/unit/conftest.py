from pytest import fixture

from application.usecases import OrderCallbackService


class FakeOrderRepo:

    def __init__(self, engine):
        self._db = engine

    async def create_order(self, info: dict):
        self._db[info['username']] = info

    async def update_order(self, username: str, info: dict):
        data = self._db[username]
        data.update(info)

    async def get_order(self, username):
        return self._db.get(username)


@fixture(scope='module')
def engine():
    return {}


@fixture(scope='module')
def order_service(engine):
    return OrderCallbackService(repo=FakeOrderRepo(engine=engine))  # type: ignore
