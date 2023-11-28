from sqlalchemy import Table, Column, Integer, TIMESTAMP, VARCHAR, SmallInteger, Float, Boolean, MetaData
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, declared_attr


class Base(DeclarativeBase):
    __abstract__ = True

    @declared_attr.directive
    def __tablename__(cls) -> str:
        return cls.__name__.lower()


class StockTable(Base):
    code: Mapped[int] = mapped_column(primary_key=True)
    parent: Mapped[int]
    ispath: Mapped[bool]
    name: Mapped[str]
    quantity: Mapped[int] = mapped_column(nullable=True)
    price: Mapped[int] = mapped_column(nullable=True)


metadata = MetaData()
activity = Table('activity', metadata,
                 Column('operation_code', Integer),
                 Column('time_', TIMESTAMP(timezone=False)),
                 Column('product_code', Integer),
                 Column('product', VARCHAR),
                 Column('quantity', SmallInteger),
                 Column('price', Float),
                 Column('sum_', Float),
                 Column('noncash', Boolean),
                 Column('return_', Boolean),
                 )