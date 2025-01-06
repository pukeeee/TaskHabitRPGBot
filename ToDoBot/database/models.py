from sqlalchemy import ForeignKey, String, BigInteger
from sqlalchemy.orm import Mapped, mapped_column, DeclarativeBase, relationship
from sqlalchemy.ext.asyncio import AsyncAttrs, async_sessionmaker, create_async_engine

from config import DB_URL

engine = create_async_engine(url = DB_URL, echo = True)
async_session = async_sessionmaker(engine)

class Base(AsyncAttrs, DeclarativeBase):
    pass

class User(Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(primary_key = True)
    tg_id = mapped_column(BigInteger)

class Task(Base):
    __tablename__ = "tasks"
    id: Mapped[int] = mapped_column(primary_key = True)
    task: Mapped[str] = mapped_column(String(100))
    user: Mapped[int] = mapped_column(ForeignKey("users.id"))
    status = mapped_column(String(50), default='pending')

async def async_main():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)