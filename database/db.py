from pathlib import Path

from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from database.models import Base


BASE_DIR = Path(__file__).resolve().parent
DATABASE_PATH = BASE_DIR / "bot.db"

DATABASE_URL = f"sqlite+aiosqlite:///{DATABASE_PATH}"


engine = create_async_engine(
    DATABASE_URL,
    echo=True,
)


async_session = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)

async def create_tables():
    async with engine.begin() as connection:
        await connection.run_sync(Base.metadata.create_all)