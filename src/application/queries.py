from sqlalchemy import text, bindparam
from sqlalchemy.ext.asyncio import AsyncEngine

from bootstrap.constants import OrderStatus


class OrderQueries:

    _FINAL_STATUSES = [OrderStatus.ACCEPTED, OrderStatus.CANCELED]

    def __init__(self, engine: AsyncEngine):
        self._engine = engine

    async def get_active_order(self, username: str):
        async with self._engine.begin() as connection:
            result = await connection.execute(
                text(
                    """
                    SELECT * FROM orders
                    WHERE username = :username
                    AND status NOT IN :status 
                    """
                ).bindparams(
                    bindparam('username', username),
                    bindparam('status', self._FINAL_STATUSES, expanding=True)
                )
            )
            data = [dict(row) for row in result.mappings()]
            return data

    async def get_orders(self, username: str, statuses: set[OrderStatus] = None):
        if not statuses:
            statuses = {OrderStatus.CREATED}
        async with self._engine.begin() as connection:
            result = await connection.execute(
                text(
                    """
                    SELECT * FROM orders
                    WHERE username = :username
                    AND status IN :status 
                    """
                ).bindparams(
                    bindparam('username', username),
                    bindparam('status', [*statuses], expanding=True)
                )
            )
            data = [dict(row) for row in result.mappings()]
            return data
