from pytest import mark, raises
import os

from sqlalchemy.exc import IntegrityError

from application.usecases import OrderStatus
from bootstrap.constants import ProductType


@mark.skipif(condition=not os.getenv('RUN_INTEGRATION', False), reason='Only run in integration stage')
class TestOrderRepository:

    async def test_create_order(self, create_order, get_order):
        await create_order()
        result = await get_order()
        assert len(result) == 1

    async def test_unique_username_order(self, create_order):
        await create_order()

        with raises(IntegrityError):
            await create_order()

    async def test_update_order(self, create_order, get_order, order_repo, username):
        desc = 'test'

        await create_order()
        await order_repo.update_order(username=username, info={
            'photo_id': '1',
            'description': desc
        })
        result = await get_order(client_name=username)
        assert result[0][4] == desc

    async def test_set_final_status(self, create_order, get_order, order_repo, username):
        await create_order()
        await order_repo.update_order(username=username, info={
            'status': OrderStatus.ACCEPTED,
        })
        await order_repo.update_order(username=username, info={
            'product_type': ProductType.SKETCH_PANEL,
        })
        result = await get_order(client_name=username)
        assert result[0][2] == str(ProductType.HANDMADE_PANEL)
        assert result[0][-2] == str(OrderStatus.ACCEPTED)
