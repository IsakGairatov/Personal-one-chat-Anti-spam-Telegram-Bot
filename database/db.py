from pathlib import Path
from config import postgress_url

from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

#BASE_DIR = Path(__file__).resolve().parent
#DATABASE_PATH = BASE_DIR / "bot.db"

#DATABASE_URL = f"sqlite+aiosqlite:///{DATABASE_PATH}"
DATABASE_URL = postgress_url



engine = create_async_engine(
    DATABASE_URL,
    echo=True,
)


async_session = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)
