from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import Integer, Index, String, Enum, DateTime, func
from bootstrap.constants import (ProductType, DeliveryType, OrderStatus)

from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class Order(Base):
    __tablename__ = 'orders'
    __table_args__ = (
        Index(
            'idx_orders_product_created',
            'username', 'status',
        ),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    username: Mapped[str] = mapped_column(String(32))
    product_type: Mapped[str] = mapped_column(Enum(ProductType))
    photo_id: Mapped[str] = mapped_column(String, nullable=True)
    description: Mapped[str] = mapped_column(String, nullable=True)
    delivery_type: Mapped[str] = mapped_column(Enum(DeliveryType), nullable=True)
    address: Mapped[str] = mapped_column(String, nullable=True)
    status: Mapped[str] = mapped_column(Enum(OrderStatus), server_default=OrderStatus.CREATED)
    created: Mapped[int] = mapped_column(DateTime, server_default=func.now())
