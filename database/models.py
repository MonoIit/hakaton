from sqlalchemy import Text
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    ...

class Databaza(Base):
    __tablename__ = 'gubkin3v'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    facultet: Mapped[str] = mapped_column(Text, nullable=False)
    napravlenie: Mapped[str] = mapped_column(Text, nullable=False)
    name: Mapped[str] = mapped_column(Text, nullable=False)
    mesta_b: Mapped[int] = mapped_column(default=0)
    mesta_cel: Mapped[int] = mapped_column(default=0)
    RF: Mapped[int] = mapped_column(nullable=True)
    nRF: Mapped[int] = mapped_column(nullable=True)
    Math: Mapped[bool] = mapped_column(nullable=True)
    Physic: Mapped[bool] = mapped_column(nullable=True)
    Infa: Mapped[bool] = mapped_column(nullable=True)
    Russian: Mapped[bool] = mapped_column(nullable=True)
    Chemistry: Mapped[bool] = mapped_column(nullable=True)
    Geography: Mapped[bool] = mapped_column(nullable=True)
    Obschestvo: Mapped[bool] = mapped_column(nullable=True)
    History: Mapped[bool] = mapped_column(nullable=True)
    Foreingh: Mapped[bool] = mapped_column(nullable=True)
    PE: Mapped[bool] = mapped_column(nullable=True)
    year_2021: Mapped[int] = mapped_column(nullable=True)
    year_2022: Mapped[int] = mapped_column(nullable=True)
    year_2023: Mapped[int] = mapped_column(nullable=True)

class user_card(Base):
    __tablename__ = 'users'

    user_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=False)
    facultet_1: Mapped[str] = mapped_column(Text, nullable=True)
    facultet_2: Mapped[str] = mapped_column(Text, nullable=True)
    facultet_3: Mapped[str] = mapped_column(Text, nullable=True)
    Math: Mapped[int] = mapped_column(nullable=True)
    Physic: Mapped[int] = mapped_column(nullable=True)
    Infa: Mapped[int] = mapped_column(nullable=True)
    Russian: Mapped[int] = mapped_column(nullable=True)
    Chemistry: Mapped[int] = mapped_column(nullable=True)
    Geography: Mapped[int] = mapped_column(nullable=True)
    Obschestvo: Mapped[int] = mapped_column(nullable=True)
    History: Mapped[int] = mapped_column(nullable=True)
    Foreingh: Mapped[int] = mapped_column(nullable=True)