# Файл, содержащий модели таблиц в базе данных


# Подключение модулей Python
from os import getenv
from dotenv import load_dotenv
from datetime import date as Date
from typing import List
from sqlalchemy import BigInteger, ForeignKey, String
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy.ext.asyncio import AsyncAttrs, create_async_engine, async_sessionmaker


# Настройка работы файла
load_dotenv()

engine = create_async_engine(url=getenv("DB_URL"))
session = async_sessionmaker(engine)


# Базовый класс для моделей
class Base(AsyncAttrs, DeclarativeBase):
    """Базовый класс для других классов базы данных"""

    pass


# Класс для описания модели таблицы "users" в базе данных
class User(Base):
    """Класс для описания модели таблицы "users" в базе данных"""

    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    tg_id = mapped_column(BigInteger)
    utc_offset: Mapped[int] = mapped_column()
    feedbacks_cnt: Mapped[int] = mapped_column()

    groups_where_creator: Mapped[List["Group"]] = relationship(
        "Group", back_populates="creator_info", foreign_keys="Group.creator"
    )
    groups_where_report_recipient: Mapped[List["Group"]] = relationship(
        "Group",
        back_populates="reports_recipient_info",
        foreign_keys="Group.reports_recipient",
    )


# Класс для описания модели таблицы "groups" в базе данных
class Group(Base):
    """Класс для описания модели таблицы "groups" в базе данных"""

    __tablename__ = "groups"

    id: Mapped[int] = mapped_column(primary_key=True)
    creator: Mapped[int] = mapped_column(ForeignKey("users.id"))
    name: Mapped[str] = mapped_column(String(25))
    reports_recipient: Mapped[int] = mapped_column(ForeignKey("users.id"))
    members: Mapped[str] = mapped_column(String(625))

    creator_info: Mapped["User"] = relationship("User", foreign_keys=[creator])
    reports_recipient_info: Mapped["User"] = relationship(
        "User", foreign_keys=[reports_recipient]
    )

    reports: Mapped[List["Report"]] = relationship(
        "Report", cascade="all, delete-orphan", back_populates="group_info"
    )


# Класс для описания модели таблицы "reports" в базе данных
class Report(Base):
    """Класс для описания модели таблицы "reports" в базе данных"""

    __tablename__ = "reports"

    id: Mapped[int] = mapped_column(primary_key=True)
    group: Mapped[int] = mapped_column(ForeignKey("groups.id"))
    date: Mapped[Date] = mapped_column()
    members: Mapped[str] = mapped_column(String(625))

    group_info: Mapped["Group"] = relationship("Group", back_populates="reports")


# Функция для создания моделей таблиц в базе данных
async def create_models() -> None:
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
