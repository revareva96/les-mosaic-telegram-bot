from bootstrap.settings import AppSettings
from bootstrap.constants import ProductType
from infrastructure.db.models import Base
from infrastructure.db.repos import OrderRepo

from pytest import fixture
from sqlalchemy import text, bindparam
from sqlalchemy.ext.asyncio import create_async_engine

metadata = Base.metadata


@fixture(scope='session')
async def async_engine():
    app_config = AppSettings()
    engine = create_async_engine(app_config.db_url)
    async with engine.begin() as conn:
        await conn.run_sync(metadata.drop_all)
        await conn.run_sync(metadata.create_all)

    yield engine

    async with engine.begin() as conn:
        await conn.run_sync(metadata.drop_all)


@fixture(scope='session')
def order_repo(async_engine):
    return OrderRepo(engine=async_engine)


@fixture()
def create_order(order_repo, username):
    async def wrapper(
            client_name: str = username
    ):
        await order_repo.create_order(
            {
                'username': client_name,
                'product_type': ProductType.HANDMADE_PANEL
            }
        )

    return wrapper


@fixture()
def get_order(async_engine, username):
    async def wrapper(
            client_name: str = username
    ):
        async with async_engine.begin() as connection:
            cursor = await connection.execute(
                text(
                    """
                    SELECT * FROM orders
                    WHERE username = :username;
                    """
                ).bindparams(
                    bindparam('username', client_name)
                )
            )
            return cursor.fetchall()

    return wrapper
