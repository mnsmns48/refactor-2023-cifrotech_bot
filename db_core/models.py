from sqlalchemy import Table, Column, Integer, TIMESTAMP, VARCHAR, SmallInteger, Float, Boolean, MetaData, BigInteger
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

guests = Table('guests', metadata,
               Column('time_', TIMESTAMP(timezone=False)),
               Column('id_', BigInteger),
               Column('fullname', VARCHAR, nullable=True),
               Column('username', VARCHAR, nullable=True)
               )

sellers = Table('sellers', metadata,
                Column('seller', VARCHAR),
                Column('time_', TIMESTAMP(False), primary_key=True),
                Column('product_type', VARCHAR),
                Column('brand', VARCHAR),
                Column('name', VARCHAR, primary_key=True),
                Column('price_1', Integer),
                Column('price_2', Integer)
                )
