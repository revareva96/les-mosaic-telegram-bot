from pytest import mark, raises
import os

from sqlalchemy.exc import IntegrityError

from application.usecases import OrderStatus
from bootstrap.constants import ProductType


@mark.skipif(condition=not os.getenv('RUN_INTEGRATION', False), reason='Only run in integration stage')
class TestOrderRepository:

    async def test_create_order(self, create_order, order_repo, username):
        await create_order()
        result = await order_repo.get_uncompleted_order(username=username)
        assert len(result) == 1

    async def test_update_order(self, create_order, order_repo, username):
        desc = 'test'

        await create_order()
        await order_repo.update_order(username=username, info={
            'photo_id': '1',
            'description': desc
        })
        result = await order_repo.get_uncompleted_order(username=username)
        assert result[0]['description'] == desc

    async def test_set_final_status(self, create_order, order_repo, username):
        await create_order()
        await order_repo.update_order(username=username, info={
            'status': OrderStatus.ACCEPTED,
        })
        result = await order_repo.get_uncompleted_order(username=username)
        assert not result
