import typing as t
from sqlalchemy import text, bindparam
from sqlalchemy.ext.asyncio import AsyncEngine

from application.usecases import OrderStatus
from infrastructure.dal.abstractions import IOrderRepo


class OrderRepo(IOrderRepo):

    def __init__(self, engine: AsyncEngine):
        self._engine = engine

    async def get_uncompleted_order(self, username: str):
        final_statuses = [OrderStatus.ACCEPTED, OrderStatus.CANCELED]
        async with self._engine.begin() as connection:
            result = await connection.execute(
                text(
                    """
                    SELECT * FROM orders
                    WHERE username = :username
                    AND status NOT IN :statuses
                    LIMIT 1
                    """
                ).bindparams(
                    bindparam('username', username),
                    bindparam('statuses', final_statuses, expanding=True)
                )
            )
            return [dict(row) for row in result.mappings()]

    async def create_order(self, info: dict[str, t.Any]):
        async with self._engine.begin() as connection:
            await connection.execute(
                text(
                    """
                    INSERT INTO orders (username, product_type)
                    VALUES (:username, :product_type)
                    """
                ).bindparams(
                    bindparam('username', info['username']),
                    bindparam('product_type', info['product_type'])
                )
            )
            await connection.commit()

    async def update_order(self, username: str, info: dict[str, t.Any]):
        final_statuses = [OrderStatus.ACCEPTED, OrderStatus.CANCELED]
        async with self._engine.begin() as connection:
            for key, value in info.items():
                await connection.execute(
                    text(
                        f"""
                        UPDATE orders
                        SET {key} = :value
                        WHERE username = :username
                        AND status NOT IN :finish_statuses
                        """
                    ).bindparams(
                        bindparam('value', value),

                        bindparam('username', username),
                        bindparam('finish_statuses', final_statuses, expanding=True)
                    ),
                )
            await connection.commit()
