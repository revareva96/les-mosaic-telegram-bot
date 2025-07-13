import typing as t
from sqlalchemy import text, bindparam
from sqlalchemy.ext.asyncio import AsyncEngine

from infrastructure.dal.abstractions import IOrderRepo
from bootstrap.constants import OrderStatus


class OrderRepo(IOrderRepo):
    _FINAL_STATUSES = [OrderStatus.ACCEPTED, OrderStatus.CANCELED]

    def __init__(self, engine: AsyncEngine):
        self._engine = engine

    async def get_uncompleted_order(self, username: str):
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
                    bindparam('statuses', self._FINAL_STATUSES, expanding=True)
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
        set_parts = [f"{key} = '{str(value)}'" for key, value in info.items()]
        set_clause = ", ".join(set_parts)
        async with self._engine.begin() as connection:
            await connection.execute(
                text(
                    f"""
                    UPDATE orders
                    SET {set_clause}
                    WHERE username = :username
                    AND status NOT IN :finish_statuses
                    """
                ).bindparams(
                    bindparam('username', username),
                    bindparam('finish_statuses', self._FINAL_STATUSES, expanding=True)
                ),
            )
            await connection.commit()
